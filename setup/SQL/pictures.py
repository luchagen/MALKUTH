import sqlite3 as sl
PICMEMORY =  sl.connect('PICTURES_MEMORY.db')


def table_exists(name):
    table_check=PICMEMORY.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'"
        ).fetchall()
    return  bool(table_check)


def channels_table():
    '''
    Table for tracking discord channels.
    [logging] describes whether the channel is screened for attachments.
    '''
    if not table_exists('MASTER_PICTURES'):
        PICMEMORY.execute("""CREATE TABLE MASTER_PICTURES(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server TEXT NOT NULL,
            channel TEXT NOT NULL,
            logging INTEGER
            )""")
        PICMEMORY.commit()


def image_filters_table():
    ''' 
    table for image filters.
    The point is to use the entries to filter what can be inserted into a library.
    We by default insert default rules (images we probably don't want to save,
    e.g. gifs from tenorgifs)
    '''
    default_rules = [
        'tenor.com'
    ]

    if not table_exists('FILTER_RULES'):
        PICMEMORY.execute("""CREATE TABLE FILTER_RULES(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_name TEXT,
            rule TEXT NOT NULL
            )""")
        PICMEMORY.execute("""INSERT INTO FILTER_RULES(
                library_name,
                rule
            ) VALUES (
                ?,
                ?
            )""",[('' for _ in default_rules),
                  default_rules])
        PICMEMORY.commit()


channels_table()
image_filters_table()
