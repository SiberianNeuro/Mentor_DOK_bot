from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold, italic, code, pre
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from db import sqlite_db
from keyboards import other_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, callback_query
import datetime


class FSMRegister(StatesGroup):
    chat_id = State()
    name = State()
    username = State()
    position = State()
    reg_time = State()


@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, text('Привет ✌  \nЯ помощник в медицинском отделе ДОК 🤖\n'
                                                     'Чтобы узнать список команд, введи */help*'), parse_mode=ParseMode.MARKDOWN_V2)
        await message.delete()
    except:
        await message.delete()

# @dp.message_handler(commands='register', state=None)
async def start_register(message: types.Message):
    read = await sqlite_db.sql_staff_chat_id_read()
    for i in read:
        for j in i:
            if message.from_user.id == j:
                read = j
    if message.from_user.id == read:
        await bot.send_message(message.from_user.id, 'Ты уже регистрировался, регистрация не требуется')
    else:
        await FSMRegister.name.set()
        await bot.send_message(message.from_user.id, 'Давай знакомиться✌️\nДля начала представься по фамилии, имени и отчеству.')

# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно')

# @dp.message_handler(state=FSMRegister.name)
async def enter_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text.title()
    await bot.send_message(message.from_user.id, str(data))
    await FSMRegister.next()
    await bot.send_message(message.from_user.id, f'Приятно познакомиться, {message.text.split()[1]}, а теперь расскажи мне, какая у тебя должность в ДОКе', reply_markup=other_kb.pos_case_button)


# @dp.message_handler(state="*")
async def enter_position(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['pos'] = callback_query.data.title()
        await FSMRegister.next()
        data['username'] = '@' + callback_query.from_user.username
        await FSMRegister.next()
        data['chat_id'] = callback_query.from_user.id
        await FSMRegister.next()
        data['reg_time'] = str(datetime.date.today())
    await bot.send_message(callback_query.from_user.id, str(data))
    await bot.send_message(callback_query.from_user.id, 'Готово')
    await sqlite_db.sql_staff_add_command(state)
    await state.finish()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(commands_start, commands=['start'])
    dp.register_message_handler(start_register, commands='register', state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(enter_name, state=FSMRegister.name)
    dp.register_callback_query_handler(enter_position, lambda x: x.data, state="*")


