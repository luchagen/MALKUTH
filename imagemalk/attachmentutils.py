# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:39:26 2023

@author: suric
"""


import sqlite3 as sl

PICMEMORY =  sl.connect('PICTURES_MEMORY.db')


def clean(table_name: str):
    ''' As the purpose of the app is to be used by others,
        always clean names to prevent sql injection !'''
    return ''.join( chr for chr in table_name if chr.isalnum() )

def get_all_pictures(name: str):
    ''' returns all pictures from a specific library'''
    try:
        qry = f"SELECT attachment FROM {clean(name)}"
        return PICMEMORY.execute(qry).fetchall()
    except sl.OperationalError:
        message = '''
            No library by this name.
             If you entered a channel/did not enter anything, check if logging was activated,
             or change the channel name to a unique name (NOT case sensitive)
        '''
        return [message]


def delete_one_picture(name: str, i):
    '''remove a picture identified by an id from a specific library.'''
    qry =f"DELETE FROM {clean(name)} WHERE id=(?)"
    PICMEMORY.execute(qry,[i])

def get_one_picture(name: str,i):
    '''get a specific picture identified by an id from a specific library'''
    qry1 = f"SELECT id FROM {clean(name)}"
    qry = f"SELECT attachment FROM {clean(name)} WHERE id=(?)"
    try:
        nbr = len(PICMEMORY.execute(qry1).fetchall())
        picture = PICMEMORY.execute(qry,[i]).fetchall()
    except sl.OperationalError:
        message = '''
            No library by this name.
             If you entered a channel/did not enter anything, check if logging was activated,
             or change the channel name to a unique name (NOT case sensitive)
        '''
        return [message]
    if picture==[]:
        return ["No images with this id. the length of this library is " + str(nbr)]
    return picture

def get_all_tables():
    '''Get all picture libraries. We exclude  '''
    tables= PICMEMORY.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables.remove(('sqlite_sequence',))
    tables.remove(('MASTER_PICTURES',))
    return [title[0] for title in tables]

def get_random_picture(name: str):
    '''Get a random password from a specific library'''
    try:
        qry = f"SELECT attachment FROM {clean(name)} ORDER BY RANDOM() LIMIT 1"
        picture = PICMEMORY.execute(qry).fetchall()
        if picture==[]:
            return ["No images in this library."]
        return picture
    except sl.OperationalError:
        message = '''
            No library by this name.
             If you entered a channel/did not enter anything, check if logging was activated,
             or change the channel name to a unique name (NOT case sensitive)
        '''
        return [message]

def store_picture(attachment: str,name: str):
    '''store a picture reference inside the wanted library'''
    cleansed=clean(name)
    if (PICMEMORY.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=(?)",
            [cleansed]).fetchall() ==[(0,)]):
        try:
            qry=f""" CREATE TABLE {clean(name)} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attachment TEXT
                ); """
            PICMEMORY.execute(qry)
        except sl.OperationalError:
            PICMEMORY.rollback()
            print("OperationalError, probably tried to create a table that already exists")
    try:
        qry= f"INSERT into {clean(name)} (attachment) values(?)"
        PICMEMORY.execute(qry,([attachment]))
    except sl.OperationalError:
        PICMEMORY.rollback()
        print('''Failed to put this attachment inside the mentioned table,
               probably the table doesn't exist''')
        return
    PICMEMORY.commit()


def check_logging(server: str , channel: str):
    '''check if logging is activated in the selected channel'''
    isactivated= PICMEMORY.execute(
        "SELECT logging FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",
        (server,channel)).fetchall()
    return bool(isactivated[0][0])

def change_logging(server: str, channel:str):
    '''change logging status of a channel '''
    if(PICMEMORY.execute("SELECT count(*) FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",
                         (server,channel)).fetchall()==[(0,)]):

        PICMEMORY.execute("INSERT into MASTER_PICTURES (server,channel,logging) values(?,?,?)",
                          ([server,channel,True]))
    else:
        if check_logging(server,channel):
            PICMEMORY.execute(
                "UPDATE MASTER_PICTURES SET logging=0 WHERE server=(?) and channel=(?)",
                (server,channel)
                )
        else:
            PICMEMORY.execute(
                "UPDATE MASTER_PICTURES SET logging=1 WHERE server=(?) and channel=(?) ",
                (server,channel)
                )
    PICMEMORY.commit()

def drop_library(name: str):
    ''' Remove a library completely from the database'''
    try:
        qry = f"DROP TABLE {clean(name)}"
        PICMEMORY.execute(qry)
        qry=f""" CREATE TABLE {clean(name)} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attachment TEXT
            ); """
        PICMEMORY.execute(qry)
        PICMEMORY.commit()
        return ''
    except sl.OperationalError:
        PICMEMORY.rollback()
        message = '''
            No library by this name.
             If you entered a channel/did not enter anything, check if logging was activated,
             or change the channel name to a unique name (NOT case sensitive)
        '''
        return [message]

def get_message_embeds(message):
    """Search each embed type object in a message to see if there is a relevant image url"""
    embeds = []
    for embedcontainer in message.embeds:
        imgurl=""
        if embedcontainer.url :
            imgurl=embedcontainer.url
        if embedcontainer.thumbnail and embedcontainer.thumbnail.proxy_url:
            imgurl=embedcontainer.thumbnail.proxy_url
        if embedcontainer.image  and embedcontainer.image.proxy_url:
            imgurl=embedcontainer.image.proxy_url
        if embedcontainer.imag and embedcontainer.image.url :
            imgurl=embedcontainer.image.url
        if embedcontainer.thumbnail and embedcontainer.thumbnail.url :
            imgurl=embedcontainer.thumbnail.url
        embeds.append(imgurl)
    return embeds

def get_message_attachments(message):
    """returns all message attachments as urls"""
    attachments =[]
    for attachment in message.attachments :
        attachments.append(attachment.url)
    return attachments
