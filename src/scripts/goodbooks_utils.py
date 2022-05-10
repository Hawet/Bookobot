# this module contains some useful functions for the goodbooks website scrapping
from asyncio import futures
import requests
from bs4 import BeautifulSoup
import sqlalchemy
import pandas as pd
import concurrent

engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')


def construnct_url(book_id):
    """
    Construct url for book with given book_id
    """
    return f'https://www.goodreads.com/book/show/{book_id}'



def get_book_desc(book_id):
    """
    Get book description by book_id
    """
    url = construnct_url(book_id)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    desc = soup.find('div', class_='readable stacked', id_='description').get_text()
    return desc



def parse_whole_goodbooks(book_id):
    """
    Parse whole goodbooks website
    """
    #books = pd.read_sql('select book_id from books',engine)
    try:
        desc = get_book_desc(book_id).replace('\'','\'\'')
        engine.execute(f'update books set descr = \'{desc}\' where book_id = {book_id}; commit;')
        print('done', book_id)
    except AttributeError:
        print('error', book_id)


def parse_whole_goodbooks_all():
    """
    Parse whole goodbooks website
    """
    books = pd.read_sql('select book_id from books',engine)
    executor = concurrent.futures.ProcessPoolExecutor(15)
    futures = [executor.submit(parse_whole_goodbooks, book_id) for book_id in books['book_id'].tolist()]
    concurrent.futures.wait(futures)



def tinker():
    """
    Test function
    """
    req = requests.get('https://www.goodreads.com/book/show/4989')
    print(req)
    print(get_book_desc(4989))



if __name__ == '__main__':
    #parse_whole_goodbooks_all()
    tinker()