import sqlalchemy
from sqlalchemy.exc import IntegrityError
engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')
import pandas as pd





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
                        'select title, book_ from books'+'\n'+

                        f'where lower(replace(title,\' \',\'\')) like lower(replace(\'%%{title}%%\',\' \',\'\')) limit 10',
                        engine)



def format_df(df):
    import tabulate
    df = tabulate.tabulate(df)
    return df



def get_book_id(title):
    return pd.read_sql(f'select book_id from books where title = \'{title}\'',engine).iloc[0,0]


def add_book(book_id,user_id):
    engine.execute(
        f'insert into ratings values({book_id},{user_id},5)'
    )
    
def get_user_id(username):
    return pd.read_sql(f'select user_id from users where username = \'{username}\'',engine).iloc[0,0]
