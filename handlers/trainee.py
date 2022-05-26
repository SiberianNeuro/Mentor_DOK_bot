from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_trainee
from aiogram.types import ReplyKeyboardRemove
from db import sqlite_db



# @dp.message_handler(commands=['Режим_работы'])
async def bot_open_command(message : types.Message):
   pass


# @dp.message_handler(commands=['Меню'])
async def menu_command(message: types.Message):
    pass


def register_handlers_trainee(dp: Dispatcher):
    dp.register_message_handler(commands_start, commands=['start', 'help'])
    dp.register_message_handler(bot_open_command, commands=['Режим_работы'])
    dp.register_message_handler(menu_command, commands=['Меню'])
