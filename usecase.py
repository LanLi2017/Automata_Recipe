import glob
import json
import os
from collections import Counter, defaultdict
from functools import partial
from itertools import groupby
from operator import itemgetter

import sqlite3


def get_pk_names(cur, table):
    ''' 
    :param cur: 
    :param table: 
    :return: {'movie': ['Mname', 'Director'], 'company': ['Cname'], 'release': ['Mname', 'Director', 'Cname']}
    '''
    return map(
        itemgetter('name'),
        filter(
            itemgetter('pk'),
            cur.execute(f'PRAGMA table_info({table!r})'),
        ),
    )


def get_fk_names(cur,table):
    rows=cur.execute(f'PRAGMA foreign_key_list({table!r})')
    rows_lists=rows.fetchall()
    rows_lists.sort(key=lambda r: (r[0],r[1]))
    fk={}
    for field_id,rows in groupby(rows_lists,lambda r:r[0]):
        # [0, 0, 'company', 'Cname', 'Cname', 'NO ACTION', 'CASCADE', 'NONE']
        # [1, 0, 'movie', 'Mname', 'Mname', 'NO ACTION', 'CASCADE', 'NONE']
        # [1, 1, 'movie', 'Director', 'Director', 'NO ACTION', 'CASCADE', 'NONE']
        for row in rows:
            fk.setdefault(row[2],[]).append(row[3])
    return fk


def cal_matching_perc(pk_values,fk_values):
    '''
    
    :param pk_values: primary keys' values
    :param fk_values: foreign keys' values
    :return: overlapping percentage between foreign keys and foreign keys
    '''
    pk_counter=Counter(pk_values)
    fk_counter=Counter(fk_values)
    matching_key= pk_counter & fk_counter
    matching_len=len(matching_key)
    perc=matching_len/len(pk_counter)
    return perc


def ICs(pk,tb,cur):
    query=f"select {','.join(pk)} from {tb}"
    values=[]
    for r in cur.execute(query):
        values.append(tuple(r))
    return values


def detect_wf():
    '''
    
    :return: percentage of matching before and after the data cleaning.
    Before the cleaning, the percentage of inclusion dependency --> {('Cname',): 1.0, ('Mname', 'Director'): 1.0}
    '''
    # before data cleaning database
    dbname='usecase.db'
    # after data cleaning database
    dbname1 = 'usecase1.db'

    conn=sqlite3.connect(dbname)
    # database after cleansing
    conn1 = sqlite3.connect(dbname1)

    tables=['movie','company','release']

    # in the further , this would be more complicated
    relation_table=dict()

    with conn:
        with conn1:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            cur1=conn1.cursor()

            # relation table is with foreign key
            # get foreign key
            for tb in tables:
                fk=get_fk_names(cur,tb)
                if fk:
                    # further construction
                    relation_table[tb]=fk
                    tables.remove(tb)
            print(f'relational table name {relation_table.keys()} --> foreign key {relation_table.values()}')

            # get primary keys
            table_pks = dict(
                zip(
                    tables,
                    map(list, map(
                        partial(get_pk_names, cur),
                        tables
                    ))
                )
            )
            '''
            we assume the schema doesn't change
            '''
            # get primary key values, foreign key values (before cleaning)
            pk_v=dict()
            fk_v=dict()
            for tb,pk in table_pks.items():
                pk_v[tuple(pk)]=ICs(pk,tb,cur)

            for tb,fk_dicts in relation_table.items():
                for tb_key,fk in fk_dicts.items():
                    fk_v[tuple(fk)]=ICs(fk,tb,cur)

            # calculate the percentage of matching before cleaning
            per_matching_bef=dict()
            for fk,values in fk_v.items():
                pk_values=pk_v[fk]
                per_matching_bef[fk]=cal_matching_perc(pk_values,values)
            print(f'Before the cleaning, the percentage of inclusion dependency --> {per_matching_bef}')

            # get primary key values, foreign key values (after cleaning)
            pk_v_af = dict()
            fk_v_af = dict()
            for tb, pk in table_pks.items():
                pk_v_af[tuple(pk)] = ICs(pk, tb, cur1)

            for tb, fk_dicts in relation_table.items():
                for tb_key, fk in fk_dicts.items():
                    fk_v_af[tuple(fk)] = ICs(fk, tb, cur1)

            # calculate the percentage of matching after cleaning
            per_matching_after = dict()
            for fk, values_af in fk_v_af.items():
                pk_values_af = pk_v_af[fk]
                per_matching_after[fk] = cal_matching_perc(pk_values_af, values_af)
            print(f'After the cleaning, the percentage of inclusion dependency --> {per_matching_after}')
    with open('percentage matching changes output.txt','w')as f:
        f.write(f'Before the cleaning, the percentage of inclusion dependency --> {per_matching_bef}\n')
        f.write(f'After the cleaning, the percentage of inclusion dependency --> {per_matching_after}')


def Automata_Recipe(dbname):
    '''
    get_fk_name(cur,table)
    -  cur: database name 
    input multiple JSON files
    :return: new JSON file 
    '''
    conn = sqlite3.connect(dbname)

    tables = ['movie', 'company', 'release']

    # in the further , this would be more complicated
    relation_table={}

    with conn:
        cur = conn.cursor()
        for tb in tables:
            fk=get_fk_names(cur,tb)
            if fk:
               relation_table= fk
               tables.remove(tb)
    # for new JSON file
    dict_list=[]

    # files=glob.glob('recipe/*.json')
    # files=os.walk('recipe')[2]
    # print(files)
    for tb in tables:
        colname=[_ for _ in relation_table[tb]]
        with open('recipe/'+tb+'.json','rt')as f:
            data=f.read()
            j_data = json.loads(data)
            for dicts in j_data:
                try:
                    if dicts.values() in colname:
                        print(dicts['columnName'])
                        dict_list.append(dicts)
                except:
                    pass
    #
    # for file in os.walk('recipe/'):
    #     print(file)
    #     file1=file.split('.')[0]
    #     colname=[_ for _ in relation_table[file1]]
    #     if file1 in tables:
    #         with open(file,'r')as f:
    #             data=f.read()
    #             j_data=json.loads(data)
    #             for dicts in j_data:
    #                 try:
    #                     if dicts['columnName'] in colname:
    #                         print(dicts['columnName'])
    #                         dict_list.append(dicts)
    #                 except:
    #                     pass
    with open('Automata_recipe.json','w')as new_f:
        new_f.write(json.dumps(dict_list,indent=4))


def main():
    # detect_wf()
    Automata_Recipe('usecase.db')


if __name__=='__main__':
    main()