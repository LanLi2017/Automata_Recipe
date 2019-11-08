import sqlite3


def get_key(con,cur,*tb_name):
    '''
    :param db_name: 
    :return: primary key, foreign key 
    '''
    try:
        with con:
            # get the primary key
            cur.execute("PRAGMA TABLE_INFO ('{}')".format(*tb_name))
            columns=[d[0] for d in cur.description]
            values=list(cur)
            values=[dict(zip(columns,value))for value in values]
            pk=[]
            for v in values:
                if v['pk']!=0:
                    pk.append(v['name'])
            # res=con.execute("select * from {} WHERE Tomatometer=0.99".format(*colname))
            # print(list(res))
            return tuple(pk)

    except sqlite3.IntegrityError:
        print("couldn't get the primary key")


def cal_matching():
    '''
    two lists of 
    :return: 
    '''

    pass


def ICs():

    # primary key: Mname, director ; movie: Mname, director
    # primary key: Cname; company: Cname
    '''
    original dataset integration constraints checking
    :return: percentage of matching count
    '''

    dbname="usecase.db"
    ic1=list(con_sql(dbname,"select Mname from movie"))
    ic2=list(con_sql(dbname,"select Mname from release"))
    total1=len(ic1)
    count1=0
    for mm in ic1:
        for mr in ic2:
            if mm==mr:
                count1+=1
    pec_ic1=count1/total1




    '''
    cleaned dataset integration constraints checking
    :return: percentage of maching count
    '''
    dbname1="usecase1.db"
    ic3 = list(con_sql(dbname1, "select Mname from movie"))
    ic4 = list(con_sql(dbname1, "select Mname from release"))
    total2 = len(ic3)
    count2 = 0
    for mm in ic3:
        print(mm)
        for mr in ic4:
            print(mr)

            if mm == mr:
                count2 += 1
    pec_ic2 = count2 / total2
    return pec_ic1,pec_ic2


def main():
    # primary key for movie: Mname, Director
    # primary key for company: Cname
    # primary key for release: Mname,Cname
    db_name='usecase.db'
    con=sqlite3.connect(db_name)
    # cur=con.cursor()
    tb_name=['movie','company','release']
    # get the keys from tables : schema traversing
    # [{'move':('Mname','Director')},...]
    # key_list=list(map(lambda tb:get_key(con,cur,tb),tb_name))
    # print(key_list)
    # tb_key = dict(zip(tb_name,key_list))
    # print(tb_key)
    con.row_factory = sqlite3.Row
    cur=con.cursor()
    cur.execute("Pragma table_info('release')")
    for row in cur:
        print(list(row))


if __name__=='__main__':
    main()