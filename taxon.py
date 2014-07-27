#!/usr/bin/python3
import sqlite3
import pickle

def Create():
    Id=dict()
    Name=dict()
    Specie=list()
    Data=list()
    Son=dict()
    Parent=dict()
    global ToDB
    ToDB=list()
    with open('./test/name','r') as In:
        Raw=list(In.readlines())
        for record in Raw:
            add=record.replace('\n','').split(sep='|')
            if add[0] not in Name or add[3]=='scientific name':
                Name[add[0]]=add[1]
    with open('./test/nodes','r') as In:
        Raw=list(In.readlines())
        for record in Raw:
            add=record.replace('\n','').split(sep=' ')
            Id[add[0]]=add[1]
            #id,rank,name
            if add[2]=='species':
                Specie.append(add[0])
    for specie in Specie:
        record=[specie,]
        while Id[specie]!='1' :
            record.append(Id[specie])
            specie=Id[specie]
        if '33090' in record:
            record.pop()
            record.pop()
            Data.append(record)
    for data in Data:
        Parent[data[0]]=set(data[1:])
        for n in range(len(data)):
            if n==0:
                pass
            if data[n] not in Son:
                Son[data[n]]=set()
            else:
                Son[data[n]].add(data[n-1])
        record=[data[0],
    return


def Database():
    con=sqlite3.connect('./test/DB')
    cur=con.cursor()
    cur.execute('create table if not exists taxon (Id text,Rank text,Name text,Son text,Parent text);')
    for line in ToDB:
        Son=' '.join(line[3])
        Parent=' '.join(line[4])
        cur.execute('insert into taxon (Id,Rank,Name,Son,Parent) values (?,?,?,?,?);',(line[0],line[1],line[2],Son,Parent))
    con.commit()
    cur.close()
    con.close()
    print('Done.\n')
    return
    
def Query():
    Querytype=input('1.by id\n2.by name\n')
    if Querytype not in ['1','2']:
        print('wrong input!\n')
        return 
    con=sqlite3.connect('./test/DB')
    cur=con.cursor()
    if Querytype=='1':
        Id=input('taxon id:\n')
        cur.execute('select * from taxon where Id=?;',(Id,))
        Result=cur.fetchall()
    elif Querytype=='2':
        Name=input('scientific name:\n')
        cur.execute('select * from taxon where Name like ?;',('%'+Name+'%',))
        Result=cur.fetchall()

    for i in Result:
        Id=i[0]
        Rank=i[1]
        Name=i[2]
        Son=i[3].split(sep=' ')
        Parent=i[4].split(sep=' ')

    print('id    : ',Id)
    print('rank  : ',Rank)
    print('name  : ',Name)
    print('parent: ','->'.join(Parent))
    print('son   : ',','.join(Son))
    cur.close()
    con.close()
    return 

work=input('1.Init database\n2.query\n')
if work=='1':
    Create()
    Database()
elif work=='2':
    Query()
else:
    print('wrong input!\n')
