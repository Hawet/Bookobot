import logging

from numpy import tile
from TOKEN import TOKEN
from aiogram import Bot, Dispatcher, executor, types
import sqlalchemy
from backend import *
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton




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
        add_kb.insert(InlineKeyboardButton(index,callback_data=book_id))
    await bot.send_message(message.from_user.id,
    format_df(titles),parse_mode='html',reply_markup=add_kb)


@dp.callback_query_handler()
async def process_callback_add(callback_query: types.CallbackQuery):

    add_book(
        callback_query.data,
        get_user_id(callback_query.from_user.username)
    )
    await bot.send_message(callback_query.from_user.id,f'Book {callback_query.data} successfully added!')







if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)