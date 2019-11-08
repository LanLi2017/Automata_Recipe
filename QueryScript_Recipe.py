import json
import sqlite3


def QueryScript(dbname):
    con=sqlite3.connect(dbname)
    cur=con.cursor()
    cur.execute("select Mname,Director from movie")
    res=[]
    for r in cur:
        res.append(r)
    print(res)
    return res
    # script="""
    # SELECT Mname from movie WHERE Tomatometer=0.99;
    # SELECT Mname FROM movie WHERE Director='Ang Lee';
    # SELECT Tomatometer FROM movie WHERE Mname='Gemini man' AND Director='Ang Lee';
    # SELECT release_date FROM release WHERE Mname='Toy story 4';
    # SELECT Rating from movie WHERE Mname='Toy story 4';
    # SELECT headquarters FROM company WHERE Cname='Walt Disney Pictures';
    # SELECT company.headquarters FROM company JOIN release ON release.Cname='Parasite;GISAENGCHUNG;Hanja';
    # SELECT FoundedDate FROM company JOIN release on release.Cname=company.Cname WHERE release_date='July 19,2019';
    # SELECT Tomatometer FROM movie JOIN release ON release.Mname=movie.Mname WHERE Cname='Paramount pictures';
    # SELECT Rating FROM movie JOIN release ON release.Mname=movie.Mname JOIN company ON company.Cname=release.Cname WHERE
    # company.headquarters='500 South Buena Vista Street,Burbank,California,United States';
    # """
    # with open('qs.txt','r')as f:
    #     res=list(map(list,map(cur.execute,f)))
    # print(res)
    # cur.executescript(script)
    #
    # script = [
    #     "SELECT Mname from movie WHERE Tomatometer=0.99;",
    #     "SELECT Mname FROM movie WHERE Director='Ang Lee';",
    #     "SELECT Tomatometer FROM movie WHERE Mname='Gemini man' AND Director='Ang Lee';",
    #     "SELECT release_date FROM release WHERE Mname='Toy story 4';",
    #     "SELECT Rating from movie WHERE Mname='Toy story 4';",
    #     "SELECT headquarters FROM company WHERE Cname='Walt Disney Pictures';",
    #     "SELECT company.headquarters FROM company JOIN release ON release.Cname=company.Cname WHERE release.Mname='Parasite;GISAENGCHUNG;Hanja';",
    #     "SELECT FoundedDate FROM company JOIN release on release.Cname=company.Cname WHERE release_date='July 19,2019';",
    #     "SELECT Tomatometer FROM movie JOIN release ON release.Mname=movie.Mname WHERE Cname='Paramount pictures';",
    #     "SELECT Rating FROM movie JOIN release ON release.Mname=movie.Mname JOIN company ON company.Cname=release.Cname WHERE company.headquarters='500 South Buena Vista Street,Burbank,California,United States';",
    #     ]
    #
    # res=list(map(list,map(cur.execute,script)))
    # print(res)


def recipe(file_path):
    colname=[]
    with open(file_path,'r')as f:
        data=json.load(f)
        for d in data:
            try:
                if d['columnName'] not in colname:
                    colname.append(d['columnName'])
            except:
                pass
    print(colname)
    return colname


def get_pk_names(cur,table):
    names=[]
    for row in cur.execute(f'PRAGMA table_info({table!r})'):
        if row['pk']:
            names.append(row['name'])
    return names


def main():
    # QueryScript('usecase.db')
    # recipe('recipe/usecase1_movie.json')
    # conn=sqlite3.connect('usecase.db')
    # tables=['movie','company','release']
    # with conn:
    #     conn.row_factory=sqlite3.Row
    #     cur=conn.cursor()
    #     table_pks={}
    #     for table in tables:
    #         table_pks[table]=get_pk_names(cur,table)
    #     print(table_pks)
    QueryScript('usecase.db')

if __name__=="__main__":
    main()
