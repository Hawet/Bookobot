# this module contains some useful functions for the goodbooks website scrapping
from asyncio import futures
import requests
from bs4 import BeautifulSoup
import sqlalchemy
import pandas as pd
import concurrent
import time



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
    print(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    desc = soup.find('div', class_='readable stacked').get_text()
    return desc



def parse_whole_goodbooks(book_id):
    """
    Parse whole goodbooks website
    """
    #books = pd.read_sql('select book_id from books',engine)
    try:
        desc = get_book_desc(book_id).replace('\'','\'\'')
        print(desc)
        engine.execute(f'update books set descr = \'{desc}\' where book_id = {book_id}; commit;')
        print('done', book_id)
    except AttributeError:
        print('error', book_id)


def parse_whole_goodbooks_all(parallel=True):
    """
    Parse whole goodbooks website
    """
    if parallel:
        books = pd.read_sql('select book_id from books where descr is null',engine)
        executor = concurrent.futures.ProcessPoolExecutor(15)
        futures = [executor.submit(parse_whole_goodbooks, book_id) for book_id in books['book_id'].tolist()]
        concurrent.futures.wait(futures)
    else:
        books = pd.read_sql('select book_id from books where descr is null',engine)
        for book_id in books['book_id'].tolist():
            parse_whole_goodbooks(book_id)
            time.sleep(2.6)            


def tinker():
    url = construnct_url(1)
    page = requests.get(url)
    print(page)

    soup = BeautifulSoup(page.content, 'html.parser')
    print(soup)
    print(soup.find('div', class_='readable stacked').get_text())


if __name__ == '__main__':
    parse_whole_goodbooks_all(parallel=False)
    