import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')


def recommend(user_id):
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
        'limit 10'
         ,engine)
    return rec_df


if __name__=='__main__':
    print(recommend(100065))