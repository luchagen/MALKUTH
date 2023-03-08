# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:39:26 2023

@author: suric
"""


import sqlite3 as sl
from random import randint

PICMEMORY =  sl.connect('PICTURES_MEMORY.db')


# always clean names to prevent sql injection !
def clean(table_name: str):
    return ''.join( chr for chr in table_name if chr.isalnum() )

def getallpictures(name: str):
    qry = "SELECT attachment FROM {}".format(clean(name))
    return PICMEMORY.execute(qry).fetchall()

def getonepicture(name: str,i):
    qry1 = "SELECT id FROM {}".format(clean(name))
    qry = "SELECT attachment FROM {} WHERE id=(?)".format(clean(name))
    nbr = len(PICMEMORY.execute(qry1).fetchall())
    picture = PICMEMORY.execute(qry,[i]).fetchall()
    
    if picture==[]:
        return (["No images with this id. the length of this library is " + str(nbr)])
    return picture

def getalltables():
    tables= PICMEMORY.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables.remove(('sqlite_sequence',))
    tables.remove(('MASTER_PICTURES',))
    return [title[0] for title in tables]

def getrandompicture(name: str):
    qry = "SELECT id FROM {}".format(clean(name))
    nbr = len(PICMEMORY.execute(qry).fetchall())
    return getonepicture(name,randint(0,nbr))

def storepicture(attachment: str,name: str):
    if (PICMEMORY.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=(?)",[name]).fetchall() ==[(0,)]):
        qry=""" CREATE TABLE {} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attachment TEXT
                ); """.format(clean(name))
        PICMEMORY.execute(qry)
    qry= ("INSERT into {} (attachment) values(?)".format(clean(name)))
    PICMEMORY.execute(qry,([attachment]))
    PICMEMORY.commit()
    
#check if logging is activated in the selected channel
def checklogging(server: str , channel: str):
    isactivated= PICMEMORY.execute("SELECT logging FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",(server,channel)).fetchall()
    if isactivated == [(1,)]: 
        return True
    else:
        return False

#change logging status of a channel 
def changelogging(server: str, channel:str):
    if(PICMEMORY.execute("SELECT count(*) FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",(server,channel)).fetchall()==[(0,)]):
        PICMEMORY.execute("INSERT into MASTER_PICTURES (server,channel,logging) values(?,?,?)",([server,channel,True]))
    else:
        if checklogging(server,channel):
            PICMEMORY.execute("UPDATE MASTER_PICTURES SET logging=0 WHERE server=(?) and channel=(?) ",(server,channel))
        else:
            PICMEMORY.execute("UPDATE MASTER_PICTURES SET logging=1 WHERE server=(?) and channel=(?) ",(server,channel))
    PICMEMORY.commit()