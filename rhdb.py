import sys
import sqlalchemy
import numpy as np
import pandas as pd
#import glob

#import the connection string
from rhdb_config import db_connstr

#tables loaded in problem 1
tables = ['Master', 'Coaches', 'AwardsPlayers']
        
#overides column datatypes during read_csv
table_dtypes = {
        'Master': {},
        'Coaches': {'notes': str},
        'AwardsPlayers': {}
        }

def debug(*args, **kwargs):
    #print(file=sys.stderr, *args, **kwargs)
    pass

# generates drop/create table scripts based upon type information in dataframe
def gen_create_table_sql(table, dtypes, uniques, maxlen):
    sql = ['DROP TABLE IF EXISTS {};'.format(table)];
    sql.append('CREATE TABLE {} ('.format(table))
    columns = list(dtypes.keys())
    for c, dtype in dtypes.items():
        coltype = 'INT'
        if dtype.kind == 'O':
            coltype = 'VARCHAR({})'.format(maxlen[c])
        elif dtype.kind == 'f':
            coltype = 'FLOAT'
        sql.append('  {} {}{}'.format(c, coltype, '' if c == columns[-1] else ','))
    sql.append(');')
    sql.append('');
    return '\n'.join(sql)
    
def load_csv(path, dtypes):
    return pd.read_csv(path, dtype=dtypes)

#extracts info for columns in dataframe
# dtypes - column datatype
# uniques - count of unique values in column
# maxlen - max length of string in string columns
def analyze_csv(table, df):
    path = 'data/' + table + '.csv'
    debug('--PATH', path)
    debug('Rows:', len(df))
    dtypes = {c:df[c].dtype for c in df.columns}
    debug('Types:', dtypes)
    uniques = {c:len(df[c].unique()) for c in df.columns}
    debug('Uniques:', uniques)

    def nlen(v):
        if type(v) == float and np.isnan(v): return 0
        return len(v)
    
    maxlen = {c:max(map(nlen,df[c])) for c, dtype in dtypes.items() if dtype.kind == 'O'}
    debug('Max Length:',maxlen)

    return dtypes, uniques, maxlen

    sql = gen_create_table_sql(table, dtypes, uniques, maxlen)

#dumps info about csv table used to help prepare table schema
def dump_table_info(table, dtypes, uniques, maxlen):
    print('TABLE',table)
    print('Col\tType\tMaxLen\tUniq')
    for c in dtypes.keys():
        print(c,dtypes[c],maxlen.get(c,''),uniques[c],sep='\t')
    print('')

#writes dataframe to db table
def load_table(db, table, df):
    db.execute('DELETE FROM {};'.format(table))
    debug('writing to db....')
    df.to_sql(table,db,index=False,if_exists='append')

#ETL scoring.csv to PlayerTeamHistory table
def etl_scoring(db):
    df = load_csv('data/Scoring.csv',table_dtypes.get('Scoring',None))
    df = df[['playerID','year','stint','tmID']] 
    load_table(db, 'PlayerTeamHistory', df)

#main entrypoint
def main(cmd):
    db = sqlalchemy.create_engine(db_connstr)
    if(cmd != 'sql'):
        debug('connecting...')
        db.connect()

    if cmd == 'etl':
        etl_scoring(db)
        return

    #for path in glob.glob('data/*.csv'):
    for table in tables:
        debug('table',table)
        debug('loading csv...')
        path = 'data/{}.csv'.format(table)
        df = load_csv(path, table_dtypes.get(table,None))
        table_info = analyze_csv(table, df)
        
        sql = gen_create_table_sql(table, *table_info)
        if(cmd == 'sql'):
            print(sql)

        if(cmd == 'dump'):
            dump_table_info(table, *table_info)

        if(cmd == 'load'):
            load_table(db, table, df)

if __name__ == "__main__":
    ## ideally we'd use something like argparse to validate command line
    ## arguments
    main(sys.argv[1])




