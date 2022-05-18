import re
import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')


def recommend(user_id, num_books=10):
    rec_df = pd.read_sql(
        'select '+
        'title, '+
        'b.book_id, '+
        'r.rating '+
        'from books b '+
        'inner join '+
        '('+
            'select book_id, '+
            'avg(rating) as rating '+
            'from ratings r '+
            'where user_id in '+
            '('+
                'select user_id '+
                'from ratings '+
                'where book_id in '+
                '( '+
                    'select book_id '+
                    'from ratings '+
                    f'where user_id = {user_id} '+
            '	) '+
            ') '+
            'group by book_id '+
        ') r '+
        'on r.book_id = r.book_id '+
        
        'where b.book_id not in '+ 
        '( '+
            'select book_id '+
            'from not_interested '+
            f'where user_id = {user_id}) '+
        ' and b.book_id not in '+ 
        '( '+
            'select book_id '+
            'from ratings '+
            f'where user_id = {user_id}) '+
        'order by r.rating desc '+
        f'limit {num_books}'
         ,engine)
    return rec_df





def recommend_single_book(user_id):
    """
    Getting siingle book from recommendation table, if exists
    """
    rec = pd.read_sql(f'select * from recommendations where user_id = {user_id}',engine)
    if rec.empty:
        return None
    else:
        return rec.iloc[0]

def construct_recommendation_table(user_id=None):
    """
    This function constructs recommendation table for given user
    or if user not provided, for all users
    """
    if user_id is None:
        users = pd.read_sql('select user_id from users', engine)['user_id'].tolist()
        res_df = pd.DataFrame(columns=['user_id', 'book_id'])
        for user in users:
            print('constructing recommendation for user: ', user)
            rec_df = recommend(user)
            rec_df['user_id'] = user
            res_df = res_df.append(rec_df)
        res_df.to_sql('recommendations', engine, if_exists='replace', index=False)
    else:
        users = pd.read_sql(f'select user_id from users where user_id={user_id}', engine)['user_id'].tolist()
        res_df = pd.DataFrame(columns=['user_id', 'book_id'])
        for user in users:
            print('constructing recommendation for user: ', user)
            rec_df = recommend(user,100)
            rec_df['user_id'] = user
            res_df = res_df.append(rec_df)
        res_df.to_sql('recommendations', engine, if_exists='append', index=False)

def delete_from_recommendation(book_id,user_id):
    engine.execute(
        f'delete from recommendations where user_id = {user_id} and book_id = {book_id}; commit;'
    )
    print(f'deleted {book_id} from {user_id}')


if __name__=='__main__':
    #print(recommend(100065))
    # testing deletion and recommendation
    #print(recommend_single_book(100065))
    #delete_from_recommendation(100065,890)
    print(recommend_single_book(100065))
    #print(construct_recommendation_table())