from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher

from loader import dp, bot

from app.filters.admin import IsAdmin
from app.db import sqlite_db
from app.keyboards import admin_kb
from app.keyboards.admin_kb import get_format_keyboard, get_status_keyboard, exam_callback, get_delete_button
from app.utils.misc.states import FSMAdmin


# Команда входа в админку
# @dp.message_handler(IsAdmin(), commands=['moderator'], state="*")
async def admin_start(m: types.Message, state: FSMContext):
    await state.finish()
    await m.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                       f'Что я умею:\n\n'
                       f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                       f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях',
                       reply_markup=admin_kb.button_case_admin)
    await m.delete()

"""Загрузка опроса"""


# Начало загрузки опроса: документ
# @dp.message_handler(IsAdmin(), text="Загрузить", state=None)
async def exam_start(m: types.Message):
    await FSMAdmin.document.set()
    await m.answer('Начинаем загрузку результатов аттестации 🤓\n'
                   'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b>',
                   reply_markup=admin_kb.button_case_cancel
                   )
    await m.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


# Отменяющий хэндлер
# @dp.message_handler(state='*', commands='Отмена')
# @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler_admin(m: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await m.reply('Принято 👌', reply_markup=admin_kb.button_case_admin)

# Загрузка документа, переход к запросу ФИО
# @dp.message_handler(IsAdmin(), content_types=['document'], state=FSMAdmin.document)
async def load_document(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['document'] = m.document.file_id
    await FSMAdmin.next()
    await m.answer('А теперь введи ФИО стажера')

# Загрузка ФИО, переход к выбору формата опроса
# @dp.message_handler(IsAdmin(), state=FSMAdmin.name)
async def load_name(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = m.text
    await FSMAdmin.next()
    await m.answer('В каком формате проходил опрос?',
                   reply_markup=get_format_keyboard()
                   )

# Выбор формата опроса, переход к выбору итога аттестации
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='format'), state=FSMAdmin.form)
async def load_form(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        data['form'] = callback_data.get("action_data")
    await FSMAdmin.next()
    await c.answer()
    await bot.send_message(c.from_user.id, 'А решение по стажеру какое?',
                           reply_markup=get_status_keyboard())


# Выбор итога аттестации, переход к загрузке ссылки
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='status'), state=FSMAdmin.status)
async def load_status(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        data['status'] = callback_data.get("action_data")
    await FSMAdmin.next()
    await c.answer()
    await bot.send_message(c.from_user.id, 'И ссылочку к видео на ютуб, пожалуйста')


# Загрузка ссылки, обёртка результатов загрузки
# @dp.message_handler(IsAdmin(), state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = message.text
    await sqlite_db.sql_add_command(state)
    read = await sqlite_db.item_search(data["document"])
    for ret in read:
        # Ответ в личные сообщения обучатору
        await bot.send_document(
            message.from_user.id, data["document"],
            caption=f'{data["name"]}\nФормат опроса: {data["form"]}\nСтатус аттестации: {data["status"]}\nСсылка YT: {data["link"]}',
            reply_markup=get_delete_button(ret[-1])
        )
        await message.answer('Готово! 👌', reply_markup=admin_kb.button_case_admin)
        # Если перевод на более высокую должность одобрен, отправить в чат к Даше Шкред
        # if ret[3] == 'Аттестация пройдена ✅' and ret[2] not in ['Опрос 4-го дня', 'Внутренний опрос']:
        #     await bot.send_document(
        #         -781832035, ret[0],
        #         caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}'
        #     )
        # # Отправка в чат "логи бота обучаторов" для контроля корректности выполнения команд
        # await bot.send_document(
        #     -1001776821827, ret[0],
        #     caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}'
        # )
    await state.finish()


# Команда на удаление опроса
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='delete'))
async def del_callback_run(c: types.CallbackQuery, callback_data: dict):
    await sqlite_db.sql_delete_command(callback_data.get("action_data"))
    await c.answer(text='Информация удалена', show_alert=True)


"""Старт поиска по базе опросов"""

# Начало поиска: запрос ФИО
# @dp.message_handler(IsAdmin(), text='Найти', state=None)
async def start_search(message: types.Message):
    # await bot.send_message(message.from_user.id, 'Выбери критерий поиска', reply_markup=admin_kb.search_button_case)
    await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                            reply_markup=admin_kb.button_case_cancel)
    await FSMAdmin.trainee_name.set()


# Поиск ФИО по БД, вывод результатов
# @dp.message_handler(IsAdmin(), state=FSMAdmin.trainee_name)
async def search_item(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainee_name'] = message.text.title()
    read = await sqlite_db.name_search(data['trainee_name'])
    if not read:
        await bot.send_message(message.from_user.id, 'Информации об этом сотруднике нет 🤔',
                                   reply_markup=admin_kb.button_case_admin)
    else:
        for ret in read:
            await bot.send_document(
                message.from_user.id, ret[0],
                caption=f'{ret[1]}\nФормат опроса:'
                        f' {ret[2]}\nСтатус аттестации:'
                        f' {ret[3]}\nСсылка YT: {ret[-3]}',
                reply_markup=get_delete_button(ret[-1])
            )
        await bot.send_message(message.from_user.id, 'Готово!👌', reply_markup=admin_kb.button_case_admin)
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, IsAdmin(), commands=['moderator'], state="*")
    dp.register_message_handler(cancel_handler_admin, IsAdmin(), commands='Отмена', state="*")
    dp.register_message_handler(cancel_handler_admin, IsAdmin(), Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(exam_start, IsAdmin(), text='Загрузить', state=None)
    dp.register_message_handler(load_document, IsAdmin(), content_types=['document'], state=FSMAdmin.document)
    dp.register_message_handler(load_name, IsAdmin(), state=FSMAdmin.name)
    dp.register_callback_query_handler(load_form, IsAdmin(), exam_callback.filter(action='format'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, IsAdmin(), exam_callback.filter(action='status'), state=FSMAdmin.status)
    dp.register_message_handler(load_link, IsAdmin(), state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, IsAdmin(), exam_callback.filter(action='delete'))
    dp.register_message_handler(start_search, IsAdmin(), text='Найти', state=None)
    dp.register_message_handler(search_item, IsAdmin(), state=FSMAdmin.trainee_name)
