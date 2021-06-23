import logging
from recomendation import recommend

from numpy import add, tile
from TOKEN import TOKEN
from aiogram import Bot, Dispatcher, executor, types
import sqlalchemy
from backend import *
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
    await bot.send_message(callback_query.from_user.id,f'Book {callback_query.data.split()[0]} successfully added!')


@dp.message_handler(commands=['get_recommendation'])
async def process_get_recommendation(message: types.message):
    titles = recommend(get_user_id(message.from_user.username))

    get_rec_kb = InlineKeyboardMarkup(row_width=5)

    for book_id,index in zip(titles['book_id'],titles.index):
        get_rec_kb.insert(InlineKeyboardButton(index,callback_data=str(book_id)+',get_rec'))
    await bot.send_message(message.from_user.id,
    format_df(titles),parse_mode='html',reply_markup=get_rec_kb)



@dp.callback_query_handler(lambda c: c.data.split(',')[1] in ['get_rec'])
async def process_callback_get_rec(callback_query: types.CallbackQuery):

    add_into_not_interested(
        get_user_id(callback_query.from_user.username),
        callback_query.data.split(',')[0]
    )
    await bot.send_message(callback_query.from_user.id,
                            f'Book {callback_query.data.split()[0]} successfully added into not_interested!'
                            )














if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)