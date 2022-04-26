from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.types import ParseMode
# from aiogram.utils.markdown import text, bold, italic, code, pre
# from create_bot import dp, bot
# from aiogram.dispatcher.filters import Text
# from db import sqlite_db
# from db.sqlite_db import sql_add_command
# from keyboards import admin_kb
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, callback_query

overlords = [323123946]


# @dp.message_handler(content_types=['animation'])
async def gif_id(message: types.Message):
    if message.from_user.id in overlords:
        await message.reply(message.animation.file_id)
    else:
        pass


# @dp.message_handler(content_types=['sticker'])
async def sticker_id(message: types.Message):
    if message.from_user.id in overlords:
        await message.reply(message.sticker.file_id)
    else:
        pass


async def photo_id(message: types.Message):
    if message.from_user.id in overlords:
        await message.reply_photo(message.photo[-1].file_id)
    else:
        pass


def register_handlers_overlord(dp: Dispatcher):
    dp.register_message_handler(photo_id, content_types=['photo'])
    dp.register_message_handler(gif_id, content_types=['animation'])
    dp.register_message_handler(sticker_id, content_types=['sticker'])
