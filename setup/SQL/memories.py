import sqlite3 as sl
MEMORY =  sl.connect('MEMORY.db')


def table_exists(name):
    table_check=MEMORY.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"
        ).fetchall()
    return  bool(table_check)


def channels_table():
    '''
    Table for tracking discord channels.
    Malkuth should behave differently depending on the channel.
    '''
    if not table_exists('CHANNELS'):
        MEMORY.execute("""CREATE TABLE CHANNELS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server TEXT NOT NULL,
            channel TEXT NOT NULL,
            system_prompt TEXT
            )""")
        MEMORY.commit()


channels_table()
