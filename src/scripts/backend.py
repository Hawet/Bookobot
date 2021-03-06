import sqlalchemy
from sqlalchemy.exc import IntegrityError
engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')
import pandas as pd
import numpy as np
from PIL import Image
import requests
import io



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
    print(f'select user_id from users where username = \'{username}\'')
    return pd.read_sql(f'select user_id from users where username = \'{username}\'',engine).iloc[0][0]



def add_into_not_interested(book_id,user_id):
    """
    Adding book to not_interested list for given user
    """
    engine.execute(
        'insert into not_interested '+
        f'values ({book_id}, {user_id}); '+
        'commit;'
    )


def add_into_to_read(book_id,user_id):
    """
    Adding book to to_read list for given user
    """
    engine.execute(
        'insert into to_read '+
        f'values ({user_id}, {book_id}); '+
        'commit;'
    )

def get_book_name(book_id):
    """
    Get book name by book_id
    """
    return pd.read_sql(f'select original_title from public.books where book_id = {book_id}',engine).iloc[0,0]


def get_book_cover(book_id):
    """
    Get book cover by book_id
    """
    url = pd.read_sql(f'select image_url from public.books where book_id = {book_id}',engine)['image_url'].iloc[0]
    img = Image.open(requests.get(url, stream=True).raw)
    # saving image to buffer
    buffer = io.BytesIO()
    img.convert('RGB').save(buffer, format="PNG")

    #img.show()
    return buffer.getbuffer()


def get_book_author(book_id) -> str:
    """
    Function returns book author by book_id
    """
    return pd.read_sql(f'select authors from public.books where book_id = {book_id}',engine).iloc[0,0]


def get_book_desc(bokk_id) -> str:
    """
    Function returns book description by book_id
    """
    return pd.read_sql(f'select descr from public.books where book_id = {bokk_id}',engine).iloc[0,0]





if __name__ == '__main__':
    print(get_book_cover(890))
    print(get_book_desc(890))