# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:39:26 2023

@author: suric
"""


import sqlite3 as sl
from logging import getLogger

class ImageLibraryHandler:
    '''Class to handle image libraries.'''
    _logger=getLogger(__name__)
    PICMEMORY =  sl.connect('PICTURES_MEMORY.db')
    def clean(self,table_name: str):
        ''' As the purpose of the app is to be used by others,
            always clean names to prevent sql injection !'''
        return ''.join( chr for chr in table_name if chr.isalnum() )

    def get_all_pictures(self,library_name: str):
        ''' returns all pictures from a specific library'''
        try:
            qry = f"SELECT attachment FROM {self.clean(library_name)}"
            return self.PICMEMORY.execute(qry).fetchall()
        except sl.OperationalError:
            message = '''
                No library by this name.
                 If you entered a channel/did not enter anything, check if logging was activated,
                 or change the channel name to a unique name (NOT case sensitive)
            '''
            self._logger.error(message)
            return [message]

    def add_exclude_rule(self,**library_rules):
        '''add a rule to exclude particular domains from image urls for a library.'''
        qry= '''INSERT INTO FILTER_RULES (library_name,rule) VALUES (?,?)'''
        try:
            self.PICMEMORY.execute(qry,list(library_rules.items()))
            self.PICMEMORY.commit()
        except Exception as e:
            self.PICMEMORY.rollback()
            self._logger.error(str(e))

    def show_exclude_rules(self,library_name):
        '''add a rule to exclude particular domains from image urls for a library.'''
        qry= '''SELECT * FROM FILTER_RULES WHERE library_name= ?'''
        try:
            self.PICMEMORY.execute(qry,[(library_name,)])
        except Exception as e:
            self._logger.error(str(e))

    def remove_exclude_rule(self,id):
        '''add a rule to exclude particular domains from image urls for a library.'''
        qry= '''DELETE FROM FILTER_RULES WHERE id= ?'''
        try:
            self.PICMEMORY.execute(qry,[(id,)])
            self.PICMEMORY.commit()
        except Exception as e:
            self.PICMEMORY.rollback()
            self._logger.error(str(e))

    def delete_one_picture(self,library_name: str, i):
        '''remove a picture identified by an id from a specific library.'''
        qry =f"DELETE FROM {self.clean(library_name)} WHERE id=(?)"
        self.PICMEMORY.execute(qry,[i])

    def get_one_picture(self,library_name: str,i):
        '''get a specific picture identified by an id from a specific library'''
        qry1 = f"SELECT id FROM {self.clean(library_name)}"
        qry = f"SELECT attachment FROM {self.clean(library_name)} WHERE id=(?)"
        try:
            nbr = len(self.PICMEMORY.execute(qry1).fetchall())
            picture = self.PICMEMORY.execute(qry,[i]).fetchall()
        except sl.OperationalError:
            message = '''
                No library by this name.
                 If you entered a channel/did not enter anything, check if logging was activated,
                 or change the channel name to a unique name (NOT case sensitive)
            '''
            self._logger.error(message)
            return [message]
        if picture==[]:
            return ["No images with this id. the length of this library is " + str(nbr)]
        return picture

    def get_all_tables(self):
        '''Get all picture libraries.
         Every table from the database '''
        tables= self.PICMEMORY.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        tables.remove(('sqlite_sequence',))
        tables.remove(('MASTER_PICTURES',))
        tables.remove(('FILTER_RULES',))
        return [title[0] for title in tables]

    def get_random_pictures(self,library_name: str,amount=1):
        '''Get a number of pictures from a specific library.
        We should not return the same picture multiple times.'''
        try:
            qry = f'''SELECT attachment FROM {self.clean(library_name)}
                    ORDER BY RANDOM() LIMIT {amount}'''
            picture = self.PICMEMORY.execute(qry).fetchall()
            if picture==[]:
                return ["No images in this library."]
            return picture
        except sl.OperationalError:
            message = '''
                No library by this name.
                 If you entered a channel/did not enter anything, check if logging was activated,
                 or change the channel name to a unique name (NOT case sensitive)
            '''
            self._logger.error(message)
            return [message]

    def store_picture(self,attachment: str,library_name: str):
        '''store a picture reference inside the wanted library'''
        cleansed=self.clean(library_name)
        if (self.PICMEMORY.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=(?)",
                [cleansed]).fetchall() ==[(0,)]):
            try:
                qry=f""" CREATE TABLE {self.clean(library_name)} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attachment TEXT NOT NULL
                    ); """
                self.PICMEMORY.execute(qry)
            except sl.OperationalError:
                self.PICMEMORY.rollback()
                print("OperationalError, probably tried to create a table that already exists")
        try:
            qry= f"INSERT into {self.clean(library_name)} (attachment) values(?)"
            self.PICMEMORY.execute(qry,([attachment]))
        except sl.OperationalError:
            self.PICMEMORY.rollback()
            print('''Failed to put this attachment inside the mentioned table,
                   probably the table doesn't exist''')
            return
        self.PICMEMORY.commit()


    def check_logging(self,server: str , channel: str):
        '''check if logging is activated in the selected channel'''
        isactivated= self.PICMEMORY.execute(
            "SELECT logging FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",
            (server,channel)).fetchall()
        return bool(isactivated[0][0])

    def change_logging(self,server: str, channel:str):
        '''change logging status of a channel '''
        if(self.PICMEMORY.execute(
            "SELECT count(*) FROM MASTER_PICTURES WHERE server=(?) AND channel=(?)",
            (server,channel)).fetchall()==[(0,)]
            ):

            self.PICMEMORY.execute(
                            "INSERT into MASTER_PICTURES (server,channel,logging) values(?,?,?)",
                              ([server,channel,True]))
        else:
            if self.check_logging(server,channel):
                self.PICMEMORY.execute(
                    "UPDATE MASTER_PICTURES SET logging=0 WHERE server=(?) and channel=(?)",
                    (server,channel)
                    )
            else:
                self.PICMEMORY.execute(
                    "UPDATE MASTER_PICTURES SET logging=1 WHERE server=(?) and channel=(?) ",
                    (server,channel)
                    )
        self.PICMEMORY.commit()

    def drop_library(self,library_name: str):
        ''' Empty a library completely '''
        try:
            qry = f"DROP TABLE {self.clean(library_name)}"
            self.PICMEMORY.execute(qry)
            qry=f""" CREATE TABLE {self.clean(library_name)} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attachment TEXT
                ); """
            self.PICMEMORY.execute(qry)
            self.PICMEMORY.commit()
            return ''
        except sl.OperationalError:
            self.PICMEMORY.rollback()
            message = '''
                No library by this name.
                 If you entered a channel/did not enter anything, check if logging was activated,
                 or change the channel name to a unique name (NOT case sensitive)
            '''
            self._logger.error(message)
            return [message]
