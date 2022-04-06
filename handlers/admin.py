from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold, italic, code, pre
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from db import sqlite_db
from db.sqlite_db import sql_add_command
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, callback_query

admins = ['siberian_neuro', 'marioneto44ka']
overlords = ['siberian_neuro']

class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()
    trainee_name = State()
    mentor_username = State()

"""Проверка на админа"""
# @dp.message_handler(commands=['moderator'])
async def make_changes_command(message: types.Message):
    global ID
    if message.from_user.username in admins:
        await bot.send_sticker(message.from_user.id, sticker='CAACAgIAAxkBAAEEYNxiTEhxKcFmVromHC2dj4qNR5qDkAACKgMAApAAAVAglpnor2dcF6MjBA')
        await bot.send_message(message.from_user.id, f'Приветствую тебя, обучатор! 🦾', reply_markup=admin_kb.button_case_admin)
        await bot.send_message(message.from_user.id, text('Что я умею:', '👉🏻 Нажми на кнопку *"Загрузить"*, чтобы передать мне информацию о прошедшей аттестации\n',
                                                      '👉🏻 Нажми кнопку *"Найти"*, чтобы найти информацию о предыдущих аттестациях', sep='\n'), parse_mode=ParseMode.MARKDOWN_V2)
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await bot.send_sticker(message.from_user.id, sticker='CAACAgQAAxkBAAEEY_tiTYxKQPLzeCweS70kX6XWr61f6wACJQ0AAufo-wL2uHDEfdtM1iME')
        await bot.send_message(message.from_user.id, 'Ты не похож на обучатора 😑\nЕсли ты и правда обучатор, обратись за пропуском к @siberian_neuro')
        await bot.delete_message(message.chat.id, message.message_id)

"""Запуск машины состояний"""
# @dp.message_handler(lambda message: message.text.startswith('Загрузить'), state=None)
async def cm_start(message : types.Message):
    if message.from_user.username in admins:
        await FSMAdmin.document.set()
        await bot.send_message(message.from_user.id, 'Начнем с протокола, загрузи его')

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
    if message.from_user.username in admins:
        async with state.proxy() as data:
            data['document'] = message.document.file_id
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'А теперь введи Ф.И.О. стажера')

"""Загрузка ФИО"""
# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.username in admins:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'В каком формате проходил опрос?', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'🟡 На И.О.', callback_data=f'Со стажера на И.О.')).\
                    add(InlineKeyboardButton(f'🔴 На врача', callback_data='С И.О. на врача')).add(InlineKeyboardButton(f'🟢 Аттестация помощника', callback_data='Со стажера L1 на сотрудника')))

"""Загрузка формата проведения опроса"""
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
async def load_form(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.username in admins:
        async with state.proxy() as data:
            data['form'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'А решение по стажеру какое?', reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton(f'😏 Прошел', callback_data=f'Аттестация пройдена ✅')).\
                    add(InlineKeyboardButton(f'😒 Не прошел', callback_data='Аттестация не пройдена ❌')))

"""Загрузка статуса опроса"""
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
async def load_status(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.username in admins:
        async with state.proxy() as data:
            data['status'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'И ссылочку к видео на ютуб, пожалуйста')

"""Ввод ссылки на ютуб и обертка результатов опроса"""
# @dp.message_handler(state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    if message.from_user.username in admins:
        async with state.proxy() as data:
            data['link'] = message.text

        # async with state.proxy() as data:
        #     await message.reply(str(data))

    await sqlite_db.sql_add_command(state)
    await state.finish()

    read = await sqlite_db.sql_read2()
    for ret in read:
        if ret[0] == fetcher:
            # await bot.send_message(message.from_user.id, f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
            await bot.send_document(message.from_user.id, ret[0], caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
            await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup(). \
                                   add(
                InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[1]}')))

"""Выловить команду инлайн кнопки"""
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} информация удалена', show_alert=True)

"""Команда инлайн кнопки"""
@dp.message_handler(commands='Удалить')
async def delete_item(message: types.Message):
    if message.from_user.username in admins:
        read = await sqlite_db.sql_read2()
        for ret in read:
            await bot.send_document(message.from_user.id, ret[0], caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
            await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup().\
                                   add(InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[1]}')))


"""Поиск по базе опросов"""

# class FSMFinder(StatesGroup):
#     trainee_name = State()


@dp.message_handler(lambda message: message.text.startswith('Найти'), state=None)
async def start_search(message: types.Message):
    if message.from_user.username in admins:
        await FSMAdmin.trainee_name.set()
        await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности')

"""Отмена загрузки"""
@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно')

@dp.message_handler(state=FSMAdmin.trainee_name)
async def search_item(message: types.Message, state: FSMContext):
    if message.from_user.username in admins:
        async with state.proxy() as data:
            data['trainee_name'] = message.text
        read = await sqlite_db.sql_read2()
        read_target = [i for i in read if data['trainee_name'] in i[1]]
        if read_target == []:
            await bot.send_sticker(message.from_user.id, sticker='CAACAgIAAxkBAAEEYONiTEoilaz930YnqFCJ1mOkt2X6SAACZwEAApAAAVAgds06eQ0IVqsjBA')
            await bot.send_message(message.from_user.id, 'Информации об этом стажере нет')
        else:
            await bot.send_sticker(message.from_user.id, sticker='CAACAgIAAxkBAAEEYOViTEpbkiPvnanRvTsdFgIng2RQUQACkwADkAABUCCcUa2lgOTMGCME')
            for ret in read_target:
                await bot.send_document(message.from_user.id, ret[0],
                                        caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
                await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup(). \
                                        add(
                    InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[1]}')))
    await state.finish()

# class FSMMentor(StatesGroup):
#     mentor = State()

@dp.message_handler(commands=['Добавить_обучатора'], state=None)
async def add_mentor(message: types.Message):
    if message.from_user.username in overlords:
        await FSMAdmin.mentor_username.set()
        await message.reply('Линкани юзернейм нового обучатора')

@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно')

@dp.message_handler(state=FSMAdmin.mentor_username)
async def append_mentor_username(message: types.Message, state: FSMContext):
    if message.from_user.username in overlords:
        async with state.proxy() as data:
            data['mentor_name'] = message.text[1:]
        admins.append(data['mentor_name'])
        await message.reply('Обучатор добавлен')
        await state.finish()






def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'])
    dp.register_message_handler(cm_start, lambda message: message.text.startswith('Загрузить'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=FSMAdmin.document)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_callback_query_handler(load_form, lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
    dp.register_message_handler(load_link, state=FSMAdmin.link)
    # dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    # dp.message_handler(delete_item, commands=['Удалить'])
