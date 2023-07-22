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
    try:
        qry = "SELECT attachment FROM {}".format(clean(name))
        return PICMEMORY.execute(qry).fetchall()
    except sl.OperationalError:
        return (["No library by this name. If you entered a channel/did not enter anything, check if logging was activated, or change the channel name to something different from what already exists (NOT case sensitive)"])
    

def deleteonepicture(name: str, i):
    qry ="DELETE FROM {} WHERE id=(?)".format(clean(name))
    PICMEMORY.execute(qry,[i])

def getonepicture(name: str,i):
    
    qry1 = "SELECT id FROM {}".format(clean(name))
    qry = "SELECT attachment FROM {} WHERE id=(?)".format(clean(name))
    try:
        nbr = len(PICMEMORY.execute(qry1).fetchall())
        picture = PICMEMORY.execute(qry,[i]).fetchall()
    except sl.OperationalError:
        return (["No library by this name. If you entered a channel/did not enter anything, check if logging was activated, or change the channel name to something different from what already exists (NOT case sensitive)"])
    if picture==[]:
        return (["No images with this id. the length of this library is " + str(nbr)])
    return picture

def getalltables():
    tables= PICMEMORY.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables.remove(('sqlite_sequence',))
    tables.remove(('MASTER_PICTURES',))
    return [title[0] for title in tables]

def getrandompicture(name: str):
    try:
        qry = "SELECT attachment FROM {} ORDER BY RANDOM() LIMIT 1".format(clean(name))
        picture = PICMEMORY.execute(qry).fetchall()
        if picture==[]:
            return (["No images in this library."])
        return picture
    except sl.OperationalError:
        return (["No library by this name. If you entered a channel/did not enter anything, check if logging was activated, or change the channel name to something different from what already exists (NOT case sensitive)"])
        
        
def storepicture(attachment: str,name: str):
    cleansed=clean(name)
    if (PICMEMORY.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=(?)",[cleansed]).fetchall() ==[(0,)]):
        try:
            qry=""" CREATE TABLE {} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attachment TEXT
                    ); """.format(clean(name))
            PICMEMORY.execute(qry)
        except sl.OperationalError:
            PICMEMORY.rollback()
            print("OperationalError, probably tried to create a table that already exists")
    try:
        qry= ("INSERT into {} (attachment) values(?)".format(clean(name)))
        PICMEMORY.execute(qry,([attachment]))
    except sl.OperationalError:
        PICMEMORY.rollback()
        print("Failed to put this attachment inside the mentioned table, probably the table doesn't exist")
        return
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
    
def droplibrary(name: str):
    try:
        qry = "DROP TABLE {}".format(clean(name))
        PICMEMORY.execute(qry)
        qry=""" CREATE TABLE {} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attachment TEXT
                    ); """.format(clean(name))
        PICMEMORY.execute(qry)
     
    except sl.OperationalError:
        PICMEMORY.rollback()
        return (["No library by this name. If you entered a channel/did not enter anything, check if logging was activated, or change the channel name to something different from what already exists (NOT case sensitive)"])
    PICMEMORY.commit()

def getMessageEmbeds(message):
    """Search each embed type object in a message to see if there is a relevant image url"""
    embeds = []
    for embedcontainer in message.embeds:
                imgurl=""
                if embedcontainer.url !=None:
                        imgurl=embedcontainer.url
                if embedcontainer.thumbnail !=None and embedcontainer.thumbnail.proxy_url!=None:
                        imgurl=embedcontainer.thumbnail.proxy_url
                if embedcontainer.image != None and embedcontainer.image.proxy_url!=None :
                        imgurl=embedcontainer.image.proxy_url
                if embedcontainer.image != None and embedcontainer.image.url!=None :
                        imgurl=embedcontainer.image.url
                if embedcontainer.thumbnail !=None and embedcontainer.thumbnail.url!=None :
                        imgurl=embedcontainer.thumbnail.url
                embeds.append(imgurl)
    return embeds

def getMessageAttachments(message):
    """returns all message attachments as urls"""
    attachments =[]
    for attachment in message.attachments :
            attachments.append(attachment.url)
    return attachments