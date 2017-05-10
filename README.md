SETUP
-----

1. Sourcing from github and setting up python environment
```
git clone git@github.com:mtadd/rhdb.git
python venv ./rhdb
cd rhdb
source bin/activate
pip3 install -r requirements.txt
```

2. Creating database and user, and grant privileges if necessary.
3. update sqlalchemy connection string in ./rhdb_config.py

```
"<dbms>+<driver>://<dbuser>:<dbpass>@<dbhost>/<database>"
```

#### Example: 

```
db_connstr = "mysql+pymysql://rhdb:rhdb@localhost/rhdb"
```


Problem 1a
----------
Create Table scripts for Masters, AwardsPlayers, Coaches:

```
python rhdb.py sql > create_tables.sql
mysql -u rhdb -p rhdb < create_tables.sql
```

Problem 1b 
----------
Load CSV's for tables in Problem 1 to Database

```
python rhdb.py load
```

Problem 2
---------
Choose another Table in dataset, and ETL.

I'm choosing Scoring.csv because it relates playerID to teamID for a given
year, which will be necessary for solving Problem 3c. The relevant columns are 
(playerID, stint?, tmID, year), so I'll just extract those columns.

```
mysql -u rhdb -p rhdb < create_etl_table.sql
python rhdb.py etl_scoring
```

Problem 3a
----------
Write a query in mysql to rank the coaches for each year by number of wins. 
Should be a query not a stored procedure

```sql
SELECT year, ifnull(w,0) wins, coachID 
FROM Coaches
ORDER BY year, wins DESC;
```

If you wanted to also include postseason wins, something like:

```sql
SELECT year, ifnull(w,0) + ifnull(postw,0) wins, coachID 
FROM Coaches
ORDER BY year, wins DESC;
```

Problem 3b
----------
Write a query in mysql to rank the player for each year for number of awards. Should be a stored procedure.

I decided to only return the playerID specified by the first argument to the
stored procedure.

```sql
DROP PROCEDURE IF EXISTS query_player_rank_by_year;

DELIMITER //
CREATE PROCEDURE query_player_rank_by_year
(IN pplayerID VARCHAR(9))
BEGIN
    CREATE TEMPORARY TABLE IF NOT EXISTS player_ranking AS
    SELECT year, playerID, rank FROM (
        SELECT year, playerID, 
        CASE 
            WHEN @prevYear = year THEN @rank := @rank + 1
            WhEN @prevYear := year THEN @rank := 1
        END as rank
        FROM
        (
            SELECT year, playerID, COUNT(*) as numAwards
            FROM AwardsPlayers
            GROUP By year, playerID
            ORDER BY year, numAwards DESC
        ) select_inner, 
        (select @rank=NULL, @prevYear=NULL) local_vars
    ) select_outer;

    SELECT year, playerID, rank
    FROM player_ranking
    WHERE playerID = pplayerID
    ORDER BY year;

    DROP TABLE IF EXISTS player_ranking;
END //
```

Problem 3c
----------
Write a query to get the details of a player who won the maximum number of awards for a year during which the coach for that team also has the maximum wins

I used temporary tables for readability, but they could be rewritten as
subselects in a single query statement.

```sql
DROP TABLE IF EXISTS tmpPlayerAwardRankByYear ;
DROP TABLE if EXISTS tmpCoachWinRankByYear;

CREATE TEMPORARY TABLE tmpPlayerAwardRankByYear
SELECT year, playerID, 
CASE 
    WHEN @prevYear = year THEN @rank := @rank + 1
    WhEN @prevYear := year THEN @rank := 1
END as rank
FROM (
    SELECT year, playerID, COUNT(*) as numAwards
    FROM AwardsPlayers
    GROUP By year, playerID
    ORDER BY year, numAwards DESC ) i, 
(select @rank=NULL, @prevYear=NULL) r;

CREATE TEMPORARY TABLE tmpCoachWinRankByYear
SELECT year, coachID, tmID,
CASE 
    WHEN @CprevYear = year THEN @Crank := @Crank + 1
    WHEN @CprevYear := year THEN @Crank := 1 
END as rank
FROM (
    SELECT year, ifnull(w,0) + ifnull(postw,0) wins, tmID, coachID 
    FROM Coaches
    ORDER BY year, wins DESC ) ci,
(select @Crank=NULL, @CprevYear=NULL) cr;

SELECT p.year, t.tmID, c.coachID tm_coachID, 
       p.rank p_award_rank, c.rank c_win_rank, m.* 
FROM Master m
JOIN tmpPlayerAwardRankByYear p ON m.playerID = p.playerID
JOIN PlayerTeamHistory t ON p.playerID = t.playerID AND p.year = t.year
JOIN tmpCoachWinRankByYear c ON t.tmID = c.tmID AND t.year = c.year
WHERE c.rank = 1 AND p.rank = 1;
```
