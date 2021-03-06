import os

from os.path import abspath, dirname
os.chdir(dirname(abspath(__file__)))

from email import message
import logging
import json
from recommendation.recomendation import recommend, recommend_single_book, delete_from_recommendation, rated_books_exist
from recommendation.collaborative_filtering_utills import construct_recommendation_table
from recommendation.binder_states import BinderStates
from numpy import add, tile
from TOKEN import TOKEN
from aiogram import Bot, Dispatcher, executor, types
import sqlalchemy
from scripts.backend import *
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, user


API_TOKEN = TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
engine = sqlalchemy.create_engine('postgresql://postgres:123@localhost/books')







@dp.message_handler(commands=['start'])
async def process_start(message: types.Message):
    await bot.send_message(message.from_user.id,
    'Welcome, bookworm! \n'+
    'Tell me what books you enjoyed, and i will tell you, what books you might enjoy'
    )
    add_user(message.from_user.id,message.from_user.username)





@dp.message_handler(commands=['add'])
async def process_add(message: types.message):
    agrs = message.get_args()
    titles = search_title(agrs)
    add_kb = InlineKeyboardMarkup(row_width=5)

    for book_id,index in zip(titles['book_id'],titles.index):
        add_kb.insert(InlineKeyboardButton(index,callback_data=str(book_id)+',add'))
    await bot.send_message(message.from_user.id,
    format_df(titles),parse_mode='html',reply_markup=add_kb)


@dp.callback_query_handler(lambda c: c.data.split(',')[1] in ['add'])
async def process_callback_add(callback_query: types.CallbackQuery):
    add_book(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )
    name = get_book_name(callback_query.data.split(',')[0])
    await bot.send_message(callback_query.from_user.id,f'Book {name} successfully added!')


@dp.message_handler(commands=['get_recommendation'])
async def process_get_recommendation(message: types.message):
    await bot.send_message(message.from_user.id,'Compiling personal recommendations...')
    titles = recommend(get_user_id(message.from_user.username))

    get_rec_kb = InlineKeyboardMarkup(row_width=5)

    for book_id,index in zip(titles['book_id'],titles.index):
        get_rec_kb.insert(InlineKeyboardButton(index,callback_data=str(book_id)+',get_rec'))
    await bot.send_message(message.from_user.id,
    format_df(titles['title'].to_frame()),parse_mode='html',reply_markup=get_rec_kb)



@dp.callback_query_handler(lambda c: c.data.split(',')[1] in ['get_rec'])
async def process_callback_get_rec(callback_query: types.CallbackQuery):

    add_into_not_interested(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )
    name = get_book_name(callback_query.data.split(',')[0])
    await bot.send_message(callback_query.from_user.id,
                            f'Book {name} successfully added into not_interested!'
                            )



@dp.message_handler(commands=['help'])
async def process_help(message: types.Message):
    await bot.send_message(message.from_user.id,
    'Commands: \n'+
    '/start - start bot \n'+
    '/add - add book \n'+
    '/get_recommendation - get recommendation \n'+
    '/help - show this help\n'+
    'This bot has been restartded'
    )




@dp.message_handler(commands=['binder'])
async def process_binder(message: types.Message):
    """
    This function is used to get the binder functionality for the user
    Tinder style book recommendation
    """
    BinderStates.main_menu.set()
    if rated_books_exist(get_user_id(message.from_user.username)):
        initial_recommendation = recommend_single_book(get_user_id(message.from_user.username))
        # Constructing recommendation table for given user if no recommendations found
        if initial_recommendation is None:
            await bot.send_message(message.from_user.id, 'No recommendations found!'+'\n'+'construncting initial recommendation table...')
            construct_recommendation_table(get_user_id(message.from_user.username))
        initial_recommendation = recommend_single_book(get_user_id(message.from_user.username))
        binder_markup = InlineKeyboardMarkup(row_width=3)
        binder_markup.insert(InlineKeyboardButton(u"\u2764\ufe0f",callback_data=str(initial_recommendation.book_id)+',binder_like,'+str(message.from_user.id)))
        binder_markup.insert(InlineKeyboardButton(u"\U0001F3F3",callback_data=str(initial_recommendation.book_id)+',binder_leave,'+str(message.from_user.id)))
        binder_markup.insert(InlineKeyboardButton(u"\u274C",callback_data=str(initial_recommendation.book_id)+',binder_dislike,'+str(message.from_user.id)))
        await bot.send_photo(message.from_user.id,get_book_cover(initial_recommendation.book_id))
        await bot.send_message(message.from_user.id,text=initial_recommendation.title)
        # send book desc if present
        if get_book_desc(initial_recommendation.book_id) is not None:
            await bot.send_message(message.from_user.id,get_book_desc(initial_recommendation.book_id))
        await bot.send_message(message.from_user.id,text=get_book_author(initial_recommendation.book_id),reply_markup=binder_markup)
    else:
        await bot.send_message(message.from_user.id, "You do not have any rated books, please use /add command to add books that you like")    

@dp.callback_query_handler(lambda c: c.data.split(',')[1] in ['binder_dislike'])
async def process_callback_binder_like(callback_query: types.CallbackQuery):
    """
    Processing dislike button
    Adding into not interestion and deleting from recommendation
    """
    

    add_into_not_interested(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )
    delete_from_recommendation(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )

    target_user_id = get_user_id(callback_query.from_user.username)
    target_chat_id = callback_query.from_user.id
    
    print(target_user_id)
    initial_recommendation = recommend_single_book(target_user_id)
    if initial_recommendation is None:
            await bot.send_message(message.from_user.id, 'No recommendations found!'+'\n'+'construncting initial recommendation table...')
            construct_recommendation_table(get_user_id(message.from_user.username))
    binder_markup = InlineKeyboardMarkup(row_width=3)
    binder_markup.insert(InlineKeyboardButton(u"\u2764\ufe0f",callback_data=str(initial_recommendation.book_id)+',binder_like,'+str(target_user_id)))
    binder_markup.insert(InlineKeyboardButton(u"\U0001F3F3",callback_data=str(initial_recommendation.book_id)+',binder_leave,'+str(target_user_id)))
    binder_markup.insert(InlineKeyboardButton(u"\u274C",callback_data=str(initial_recommendation.book_id)+',binder_dislike,'+str(target_user_id)))
    await bot.send_photo(callback_query.from_user.id,get_book_cover(initial_recommendation.book_id))
    await bot.send_message(callback_query.from_user.id,text=initial_recommendation.title)
    # send book desc if present
    if get_book_desc(initial_recommendation.book_id) is not None:
        await bot.send_message(callback_query.from_user.id,get_book_desc(initial_recommendation.book_id))
    await bot.send_message(callback_query.from_user.id,text=get_book_author(initial_recommendation.book_id),reply_markup=binder_markup)
    


@dp.callback_query_handler(lambda c: c.data.split(',')[1] in ['binder_like'])
async def process_callback_binder_like(callback_query: types.CallbackQuery):
    """
    Processing like button
    """
    add_into_to_read(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )

    delete_from_recommendation(
        callback_query.data.split(',')[0],
        get_user_id(callback_query.from_user.username)
    )

    target_user_id = get_user_id(callback_query.from_user.username)
    target_chat_id = callback_query.from_user.id
    
    print(target_user_id)
    initial_recommendation = recommend_single_book(target_user_id)
    if initial_recommendation is None:
            await bot.send_message(message.from_user.id, 'No recommendations found!'+'\n'+'construncting initial recommendation table...')
            construct_recommendation_table(get_user_id(message.from_user.username))
    binder_markup = InlineKeyboardMarkup(row_width=3)
    binder_markup.insert(InlineKeyboardButton(u"\u2764\ufe0f",callback_data=str(initial_recommendation.book_id)+',binder_like,'+str(target_user_id)))
    binder_markup.insert(InlineKeyboardButton(u"\U0001F3F3",callback_data=str(initial_recommendation.book_id)+',binder_leave,'+str(target_user_id)))
    binder_markup.insert(InlineKeyboardButton(u"\u274C",callback_data=str(initial_recommendation.book_id)+',binder_dislike,'+str(target_user_id)))
    await bot.send_photo(callback_query.from_user.id,get_book_cover(initial_recommendation.book_id))
    await bot.send_message(callback_query.from_user.id,text=initial_recommendation.title)
    # send book desc if present
    if get_book_desc(initial_recommendation.book_id) is not None:
        await bot.send_message(callback_query.from_user.id,get_book_desc(initial_recommendation.book_id))
    await bot.send_message(callback_query.from_user.id,text=get_book_author(initial_recommendation.book_id),reply_markup=binder_markup)
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)