from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from db import sqlite_db
from db.sqlite_db import sql_add_command
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, callback_query

ID = None

class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()

"""Проверка на админа"""
# @dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Ну же, приказывайте', reply_markup=admin_kb.button_case_admin)
    await message.delete()

"""Запуск машины состояний"""
# @dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message : types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.document.set()
        await bot.send_message(message.from_user.id, 'Загрузи протокол')

"""Отмена загрузки"""
# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно')

"""Загрузка протокола"""
# @dp.message_handler(content_types=['document'], state=FSMAdmin.document)
async def load_document(message: types.Message, state: FSMContext):
    global fetcher
    fetcher = message.document.file_id
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['document'] = message.document.file_id
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'А теперь введи Ф.И.О. стажера')

"""Загрузка ФИО"""
# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'Каков статус опроса?', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'На И.О.', callback_data=f'Со стажера на И.О.')).\
                    add(InlineKeyboardButton(f'На врача', callback_data='С И.О. на врача')))

"""Загрузка формата проведения опроса"""
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
async def load_form(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id == ID:
        async with state.proxy() as data:
            data['form'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'Каков статус опроса?', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'Прошел', callback_data=f'Аттестация пройдена')).\
                    add(InlineKeyboardButton(f'Не прошел', callback_data='Аттестация не пройдена')))

"""Загрузка статуса опроса"""
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
async def load_status(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id == ID:
        async with state.proxy() as data:
            data['status'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'И ссылочку к видео на ютуб, пожалуйста')

"""Загрузка ссылки на ютуб"""
# @dp.message_handler(state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['link'] = message.text

        async with state.proxy() as data:
            await message.reply(str(data))

    await sqlite_db.sql_add_command(state)
    await state.finish()

    read = await sqlite_db.sql_read2()
    for ret in read:
        if ret[0] == fetcher:
            await bot.send_message(message.from_user.id, f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
            await bot.send_document(message.from_user.id, ret[0])

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} информация удалена', show_alert=True)

@dp.message_handler(commands='Удалить')
async def delete_item(message: types.Message):
    if message.from_user.id == ID:
        read = await sqlite_db.sql_read2()
        for ret in read:
            await bot.send_message(message.from_user.id, f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
            await bot.send_document(message.from_user.id, ret[0])
            await bot.send_message(message.from_user.id, text='^^^^', reply_markup=InlineKeyboardMarkup().\
                                   add(InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[1]}')))



def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=FSMAdmin.document)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_callback_query_handler(load_form, lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
    dp.register_message_handler(load_link, state=FSMAdmin.link)
    # dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    # dp.message_handler(delete_item, commands=['Удалить'])
    dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)