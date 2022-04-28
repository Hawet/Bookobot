import sqlalchemy
from sqlalchemy.exc import IntegrityError
engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')
import pandas as pd
import numpy as np




def add_user(chat_id,username):
    """ 
    Add user into active bot users, 
    if user is present than skip addition
    """
    try:
        engine.execute(
            f'insert into users(chat_id,username) values(\'{chat_id}\',\'{username}\')'
        )
    except IntegrityError:
        pass



def search_title(title):
    """
    Searching title, returns dataframe
    """
    return pd.read_sql(
                        'select title, book_id from books'+'\n'+

                        f'where lower(replace(title,\' \',\'\')) like lower(replace(\'%%{title}%%\',\' \',\'\')) limit 10',
                        engine)



def format_df(df):
    import tabulate
    from prettytable import PrettyTable
    table = PrettyTable([''] + list(df.columns))
    for row in df.itertuples():
        table.add_row(row)
    return str(table)




def get_book_id(title):
    """
    get book id by title
    """
    return pd.read_sql(f'select book_id from books where title = \'{title}\'',engine).iloc[0,0]


def add_book(book_id,user_id):
    '''
    Adding book for user with rating 5
    '''
    engine.execute(
        f'insert into ratings values({book_id},{user_id},5)'
    )
    
def get_user_id(username):
    """
    get user id by username
    """
    return pd.read_sql(f'select user_id from users where username = \'{username}\'',engine).iloc[0,0]



def add_into_not_interested(book_id,user_id):
    """
    Adding book to not_interested list for given user
    """
    engine.execute(
        'insert into not_interested '+
        f'values ({book_id}, {user_id}); '+
        'commit;'
    )


def get_book_name(book_id):
    """
    Get book name by book_id
    """
    return pd.read_sql(f'select original_title from public.books where book_id = {book_id}',engine).iloc[0,0]