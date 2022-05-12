from typing import Any, Coroutine

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from db import sqlite_db
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import simple_cal_callback, SimpleCalendar
from datetime import datetime


admins = [323123946, 555185558, 538133074]


class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()
    trainee_name = State()
    start_date = State()
    end_date = State()

"""Проверка на админа"""


# @dp.message_handler(commands=['moderator'])
async def make_changes_command(message: types.Message):
    if message.from_user.id in admins:
        await message.answer_sticker(sticker='CAACAgIAAxkBAAEEYNxiTEhxKcFmVromHC2dj4qNR5qDkAACKgMAApAAAVAglpnor2dcF6MjBA')
        await message.answer(f'Приветствую тебя, обучатор! 🦾', reply_markup=admin_kb.button_case_admin)
        await message.answer(f'Что я умею:\n\n'
                             f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n\n'
                             f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях\n\n'
                             f'👉🏻 Нажми кнопку <b>"Отчет"</b>, чтобы посмотреть на информацию о всех переводах')
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await message.answer_sticker(sticker='CAACAgQAAxkBAAEEY_tiTYxKQPLzeCweS70kX6XWr61f6wACJQ0AAufo-wL2uHDEfdtM1iME')
        await message.answer('Ты не похож на обучатора 😑\nЕсли ты и правда обучатор, обратись за пропуском к @siberian_neuro')
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(-1001776821827, f'@{message.from_user.username} хочет получить доступ к панели управления обучаторов.')

"""Запуск машины состояний"""


# @dp.message_handler(lambda message: message.text.startswith('Загрузить'), state=None)
async def cm_start(message: types.Message):
    if message.from_user.id in admins:
        await FSMAdmin.document.set()
        await bot.send_message(message.from_user.id,
                               'Начинаем загрузку результатов аттестации 🤓\n'
                               'Чтобы выйти из режима загрузки, нажми кнопку "Отмена"',
                               reply_markup=admin_kb.button_case_cancel)
        await bot.send_message(message.from_user.id, 'Сейчас тебе нужно прислать мне протокол опроса 📜')

"""Отмена загрузки"""


# @dp.message_handler(state='*', commands='Отмена')
# @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Принято 👌', reply_markup=admin_kb.button_case_admin)

"""Загрузка протокола"""


# @dp.message_handler(content_types=['document'], state=FSMAdmin.document)
async def load_document(message: types.Message, state: FSMContext):
    global fetcher
    fetcher = message.document.file_id
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['document'] = message.document.file_id
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'А теперь введи Ф.И.О. стажера')

"""Загрузка ФИО"""


# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'В каком формате проходил опрос?',
                               reply_markup=admin_kb.button_stage_full)

"""Загрузка формата проведения опроса"""


# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
async def load_form(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in admins:
        async with state.proxy() as data:
            data['form'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'А решение по стажеру какое?',
                               reply_markup=admin_kb.button_outcome_full)

"""Загрузка статуса опроса"""


# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
async def load_status(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in admins:
        async with state.proxy() as data:
            data['status'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'И ссылочку к видео на ютуб, пожалуйста')

"""Ввод ссылки на ютуб и обертка результатов опроса"""


# @dp.message_handler(state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['link'] = message.text
    await sqlite_db.sql_add_command(state)
    await state.finish()

    read = await sqlite_db.item_search()
    for ret in read:
        if ret[0] == fetcher:
            await bot.send_document(message.from_user.id, ret[0],\
                                    caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}',\
                                    reply_markup=admin_kb.button_case_admin)
            await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup(). \
                                   add(
                InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[-1]}')))
            await bot.send_document(-1001776821827, ret[0],
                                    caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}')


"""Выловить команду инлайн кнопки"""


# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'Информация удалена', show_alert=True)

"""Старт поиска по базе опросов"""


# @dp.message_handler(lambda message: message.text.startswith('Найти'), state=None)
async def start_search(message: types.Message):
    if message.from_user.id in admins:
        await FSMAdmin.trainee_name.set()
        await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности', reply_markup=admin_kb.button_case_cancel)


"""Вывод результатов поиска"""


# @dp.message_handler(state=FSMAdmin.trainee_name)
async def search_item(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['trainee_name'] = message.text
        read = await sqlite_db.item_search()
        read_target = [i for i in read if data['trainee_name'] in i[1]]
        if not read_target:
            await bot.send_animation(message.from_user.id, 'CgACAgQAAxkBAAIKFmJZQxoTG2PLqOk4KccHjiHWYmR3AAJpAgACKDSNUnucmCkxyK3TIwQ')
            await bot.send_message(message.from_user.id, 'Информации об этом стажере нет 🤔', reply_markup=admin_kb.button_case_admin)
        else:
            for ret in read_target:
                await bot.send_document(message.from_user.id, ret[0],
                                        caption=f'{ret[1]}\nФормат опроса:'
                                                f' {ret[2]}\nСтатус аттестации:'
                                                f' {ret[3]}\nСсылка YT: {ret[-3]}')
                await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup().\
                                        add(
                    InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[-1]}')))
            await bot.send_message(message.from_user.id, 'Готово!👌', reply_markup=admin_kb.button_case_admin)
    await state.finish()

def report_parser(s_d: dict, e_d: dict, slice_t: list, slice_l: list, slice_d: list):
    string_t = '\n'.join(slice_t)
    string_l = '\n'.join(slice_l)
    string_d = '\n'.join(slice_d)
    outcome_string = f'За период с <b>{s_d}</b> по <b>{e_d}</b> было проведено:\n'\
                     f'\n'\
                     f'<u>{len(slice_t)} перевода(-ов) со стажера на И.О.:</u>\n' \
                     f'{string_t}\n'\
                     f'\n'\
                     f'<u>{len(slice_d)} перевода(-ов) с И.О. на врача:</u>\n' \
                     f'{string_d}\n'\
                     f'\n'\
                     f'<u>{len(slice_l)} перевода(-ов) на специалиста L1:</u>\n' \
                     f'{string_l}\n'\
                     f'\n'\
                     f'Всего за указанный период было переведено {len(slice_l) + len(slice_l) + len(slice_d)} сотрудника(-ов) 🤩'
    return outcome_string

async def slice_report_start(message: types.Message):
    if message.from_user.id in admins:
        await FSMAdmin.start_date.set()
        await message.answer('Начинаем выгрузку среза по опросам', reply_markup=admin_kb.button_case_cancel)
        await message.answer('Выбери начальную дату: ', reply_markup=await SimpleCalendar().start_calendar())

async def slice_report_next(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_query.from_user.id in admins:
        selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
        if selected:
            await state.update_data(start_date=date.strftime('%Y-%m-%d'))
        await callback_query.answer()
        await callback_query.message.delete()
        await state.reset_state(with_data=False)
        await callback_query.message.answer('Выбери конечную дату: ',
                                                reply_markup=await SimpleCalendar().start_calendar())

async def slice_report_final(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_query.from_user.id in admins:
        selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
        if selected:
            await FSMAdmin.end_date.set()
            await state.update_data(end_date=date.strftime("%Y-%m-%d"))
        await callback_query.message.delete()
        await state.reset_state(with_data=False)
        slice_report_data = await state.get_data()
        slice_report_trainee = [i[0] for i in await sqlite_db.sql_report_trainee(slice_report_data['start_date'], slice_report_data['end_date'])]
        slice_report_l1 = [i[0] for i in await sqlite_db.sql_report_l1(slice_report_data['start_date'], slice_report_data['end_date'])]
        slice_report_doc = [i[0] for i in await sqlite_db.sql_report_doc(slice_report_data['start_date'], slice_report_data['end_date'])]
        await callback_query.message.answer(report_parser(slice_report_data['start_date'], slice_report_data['end_date'],
                                                          slice_report_trainee, slice_report_l1, slice_report_doc), reply_markup=admin_kb.button_case_admin)



def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'])
    dp.register_message_handler(cm_start, lambda message: message.text.startswith('Загрузить'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=FSMAdmin.document)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_callback_query_handler(load_form, lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
    dp.register_message_handler(load_link, state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    dp.register_message_handler(start_search, lambda message: message.text.startswith('Найти'), state=None)
    dp.register_message_handler(search_item, state=FSMAdmin.trainee_name)
    dp.register_message_handler(slice_report_start, lambda message: message.text.startswith('Отчет'), state=None)
    dp.register_callback_query_handler(slice_report_next, simple_cal_callback.filter(), state=FSMAdmin.start_date)
    dp.register_callback_query_handler(slice_report_final, simple_cal_callback.filter())