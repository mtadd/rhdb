DROP TABLE IF EXISTS Master;
CREATE TABLE Master (
  playerID VARCHAR(9),
  coachID VARCHAR(10),
  hofID VARCHAR(10),
  firstName VARCHAR(14),
  lastName VARCHAR(18),
  nameNote VARCHAR(35),
  nameGiven VARCHAR(29),
  nameNick VARCHAR(39),
  height FLOAT,
  weight FLOAT,
  shootCatch VARCHAR(1),
  legendsID VARCHAR(7),
  ihdbID FLOAT,
  hrefID VARCHAR(10),
  firstNHL FLOAT,
  lastNHL FLOAT,
  firstWHA FLOAT,
  lastWHA FLOAT,
  pos VARCHAR(3),
  birthYear FLOAT,
  birthMon FLOAT,
  birthDay FLOAT,
  birthCountry VARCHAR(19),
  birthState VARCHAR(14),
  birthCity VARCHAR(23),
  deathYear FLOAT,
  deathMon FLOAT,
  deathDay FLOAT,
  deathCountry VARCHAR(14),
  deathState VARCHAR(2),
  deathCity VARCHAR(24)
);
DROP TABLE IF EXISTS Coaches;
CREATE TABLE Coaches (
  coachID VARCHAR(10),
  year INT,
  tmID VARCHAR(3),
  lgID VARCHAR(4),
  stint INT,
  notes VARCHAR(25),
  g FLOAT,
  w FLOAT,
  l FLOAT,
  t FLOAT,
  postg FLOAT,
  postw FLOAT,
  postl FLOAT,
  postt FLOAT
);
DROP TABLE IF EXISTS AwardsPlayers;
CREATE TABLE AwardsPlayers (
  playerID VARCHAR(9),
  award VARCHAR(20),
  year INT,
  lgID VARCHAR(3),
  note VARCHAR(16),
  pos VARCHAR(2)
);
