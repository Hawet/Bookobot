# this module contains scripts and fucntions for collaborative filtering recommendation preparation
# preparation of the data
import sqlalchemy
import pandas as pd
import numpy as np

engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')



def get_book_id(title):
    """
    get book id by title
    """
    return pd.read_sql(f'select book_id from books where title = \'{title}\'',engine).iloc[0,0]



def prepare_corr_dataset():
    """
    This function fills tables 
    book_rating and corr_matrix in db for collaborative filtering
    """
    merged_data = pd.read_sql(
    'select * from books inner join ratings on books.book_id = ratings.book_id',engine
    )
    book_rating = pd.pivot_table(merged_data, index='user_id', values='rating', columns='title', fill_value=0)
    book_rating.to_sql('book_rating',engine,if_exists='replace')


def get_recommendation_collabarative(user_id,book_corr,book_rating):

    """
    constructing recommnedation table for user_id
    """

    # preparing complete book list
    book_list=  list(book_rating)
    book_titles =[] 
    for i in range(len(book_list)):
        book_titles.append(book_list[i])
    
    # getting user's ratings and not interested books
    books_list = pd.read_sql(f'select title from books where book_id in (select book_id from ratings where user_id = {user_id})',engine)['title'].to_list()
    not_interested_list = pd.read_sql(f'select books.title from not_interested inner join books on not_interested.book_id = books.book_id where not_interested.user_id = {user_id}',engine)['title'].to_list()
    
    similar_books = np.zeros(book_corr.shape[0])
    
    for book in books_list:    
        book_index = book_titles.index(book)
        similar_books += book_corr[book_index] 
    book_preferences = pd.DataFrame(columns=['user_id','book_id','title','rating'])
    for i in range(len(book_titles)):
        if (book_titles[i] not in books_list 
            and book_titles[i] not in not_interested_list
            and similar_books[i] > -0.2): # here we have arbitrary threshold for similarity (can be tweaked)
            print('current_title',book_titles[i])
            try:
                """
                catching exception for books with no title
                """
                book_preferences = book_preferences.append({
                    'user_id':user_id,
                    'book_id':get_book_id(book_titles[i]),
                    'title': book_titles[i],
                    'rating': similar_books[i]}, ignore_index=True)
            except:
                print('error')
    return book_preferences.sort_values(by='rating',ascending=False)


def construct_recommendation_table(user_id=None):
    """
    this function fills recommendation table
    for collaborative filtering
    """
    prepare_corr_dataset()
    
    book_rating = pd.read_sql('select * from book_rating',engine)
    corr_matrix = np.corrcoef(book_rating.T)

    users = pd.read_sql('select user_id from users',engine)['user_id'].tolist()

    # truncating recommendations table
    
    if user_id is None:
        engine.execute('truncate table recommendations;')
        for user in users:
            print('constructing recommendation for user: ', user)
            rec_df = get_recommendation_collabarative(user,corr_matrix,book_rating)
            rec_df['user_id'] = user
            rec_df.to_sql('recommendations',engine,if_exists='append',index=False)
    else:
        engine.execute(f'delete from recommendations where user_id = {user_id};')
        rec_df = get_recommendation_collabarative(user_id,corr_matrix,book_rating)
        rec_df['user_id'] = user_id
        rec_df.to_sql('recommendations',engine,if_exists='append',index=False)    



if __name__=='__main__':
    construct_recommendation_table()
    #prepare_corr_dataset()
