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
from keyboards.admin_kb import get_format_keyboard, get_status_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, callback_query
import datetime

admins = [323123946, 555185558, 538133074,]


class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()
    date = State()
    trainee_name = State()
    mentor_username = State()


"""Проверка на админа"""


@dp.message_handler(commands=['moderator'])
async def make_changes_command(message: types.Message):
    if message.from_user.id in admins:
        await bot.send_sticker(message.from_user.id,
                               sticker='CAACAgIAAxkBAAEEYNxiTEhxKcFmVromHC2dj4qNR5qDkAACKgMAApAAAVAglpnor2dcF6MjBA')
        await bot.send_message(message.from_user.id, f'Приветствую тебя, обучатор! 🦾',
                               reply_markup=admin_kb.button_case_admin)
        await bot.send_message(message.from_user.id, text('Что я умею:',
                                                          '👉🏻 Нажми на кнопку *"Загрузить"*, чтобы передать мне информацию о прошедшей аттестации\n',
                                                          '👉🏻 Нажми кнопку *"Найти"*, чтобы найти информацию о предыдущих аттестациях',
                                                          sep='\n'), parse_mode=ParseMode.MARKDOWN_V2)
        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await bot.send_sticker(message.from_user.id,
                               sticker='CAACAgQAAxkBAAEEY_tiTYxKQPLzeCweS70kX6XWr61f6wACJQ0AAufo-wL2uHDEfdtM1iME')
        await bot.send_message(message.from_user.id,
                               'Ты не похож на обучатора 😑\nЕсли ты и правда обучатор, обратись за пропуском к @siberian_neuro')
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(-1001776821827,
                               f'@{message.from_user.username} хочет получить доступ к панели управления обучаторов.')


"""Запуск машины состояний"""


@dp.message_handler(lambda message: message.text.startswith('Загрузить'), state=None)
async def cm_start(message: types.Message):
    if message.from_user.id in admins:
        await FSMAdmin.document.set()
        await bot.send_message(message.from_user.id,
                               'Начинаем загрузку результатов аттестации 🤓\n'
                               'Чтобы выйти из режима загрузки, нажми кнопку "Отмена"',
                               reply_markup=admin_kb.button_case_cancel)
        await bot.send_message(message.from_user.id, 'Сейчас тебе нужно прислать мне протокол опроса 📜')


"""Отмена загрузки"""


@dp.message_handler(state='*', commands='Отмена')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Принято 👌', reply_markup=admin_kb.button_case_admin)


"""Загрузка протокола"""


@dp.message_handler(content_types=['document'], state=FSMAdmin.document)
async def load_document(message: types.Message, state: FSMContext):
    global fetcher
    fetcher = message.document.file_id
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['document'] = message.document.file_id
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'А теперь введи Ф.И.О. стажера')


"""Загрузка ФИО"""


@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, 'В каком формате проходил опрос?',
                               reply_markup=get_format_keyboard())


"""Загрузка формата проведения опроса"""


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('format'), state=FSMAdmin.form)
async def load_form(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in admins:
        async with state.proxy() as data:
            data['form'] = callback_query.data.replace("format: ", "")
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'А решение по стажеру какое?',
                               reply_markup=get_status_keyboard())


"""Загрузка статуса опроса"""


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('Аттестация'), state=FSMAdmin.status)
async def load_status(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id in admins:
        async with state.proxy() as data:
            data['status'] = callback_query.data
        await FSMAdmin.next()
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, 'И ссылочку к видео на ютуб, пожалуйста')


"""Ввод ссылки на ютуб и обертка результатов опроса"""


@dp.message_handler(state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['link'] = message.text
        await FSMAdmin.next()
        async with state.proxy() as data:
            data['date'] = str(datetime.date.today())
    await sqlite_db.sql_add_command(state)
    await state.finish()

    read = await sqlite_db.item_search()
    for ret in read:
        if ret[0] == fetcher:
            # Ответ в личные сообщения обучатору
            await bot.send_document(
                message.from_user.id, ret[0],
                caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}',
                reply_markup=admin_kb.button_case_admin
            )
            await bot.send_message(
                message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[-1]}')
                )
            )
            # Если аттестация пройдена, отправить в чат к Даше Шкред
            if ret[3] == 'Аттестация пройдена ✅' and ret[2] not in ['Опрос 4-го дня', 'Внутренний опрос']:
                await bot.send_document(
                    -781832035, ret[0],
                    caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}'
                )
                await bot.send_document(
                    -1001776821827, ret[0],
                    caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}'
                )
            # Отправка в чат "логи бота обучаторов" для контроля корректности выполнения команд
            await bot.send_document(
                -1001776821827, ret[0],
                caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-3]}'
            )


# """Команда инлайн кнопки"""
#
#
# @dp.message_handler(commands='Удалить')
# async def delete_item(message: types.Message):
#     if message.from_user.id in admins:
#         read = await sqlite_db.sql_read2()
#         for ret in read:
#             await bot.send_document(message.from_user.id, ret[0], caption=f'{ret[1]}\nФормат опроса: {ret[2]}\nСтатус аттестации: {ret[3]}\nСсылка YT: {ret[-1]}')
#             await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup().\
#                                    add(InlineKeyboardButton(f'Удалить запись аттестации', callback_data=f'del {ret[1]}')))

"""Выловить команду инлайн кнопки"""


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text='Информация удалена', show_alert=True)


"""Старт поиска по базе опросов"""


@dp.message_handler(lambda message: message.text.startswith('Найти'), state=None)
async def start_search(message: types.Message):
    if message.from_user.id in admins:
        # await bot.send_message(message.from_user.id, 'Выбери критерий поиска', reply_markup=admin_kb.search_button_case)
        await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                            reply_markup=admin_kb.button_case_cancel)
        await FSMAdmin.trainee_name.set()


@dp.message_handler(state='*', commands='Отмена')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Принято 👌', reply_markup=admin_kb.button_case_admin)


"""Вывод результатов поиска"""


@dp.message_handler(state=FSMAdmin.trainee_name)
async def search_item(message: types.Message, state: FSMContext):
    if message.from_user.id in admins:
        async with state.proxy() as data:
            data['trainee_name'] = message.text
        read = await sqlite_db.item_search()
        read_target = [i for i in read if data['trainee_name'] in i[1]]
        if not read_target:
            await bot.send_animation(message.from_user.id,
                                     'CgACAgQAAxkBAAIKFmJZQxoTG2PLqOk4KccHjiHWYmR3AAJpAgACKDSNUnucmCkxyK3TIwQ')
            await bot.send_message(message.from_user.id, 'Информации об этом стажере нет 🤔',
                                   reply_markup=admin_kb.button_case_admin)
        else:
            for ret in read_target:
                await bot.send_document(message.from_user.id, ret[0],
                                        caption=f'{ret[1]}\nФормат опроса:'
                                                f' {ret[2]}\nСтатус аттестации:'
                                                f' {ret[3]}\nСсылка YT: {ret[-3]}')
                await bot.send_message(message.from_user.id, text='Опции:', reply_markup=InlineKeyboardMarkup(). \
                                       add(
                    InlineKeyboardButton(text='Удалить запись аттестации', callback_data=f'del {ret[-1]}')))
            await bot.send_message(message.from_user.id, 'Готово!👌', reply_markup=admin_kb.button_case_admin)
    await state.finish()


"""Добавление нового обучатора"""


# @dp.message_handler(commands=['Добавить_обучатора'], state=None)
# async def add_mentor(message: types.Message):
#     if message.from_user.id in overlords:
#         await FSMAdmin.mentor_username.set()
#         await message.reply('Линкани юзернейм нового обучатора')
#
#
# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#     await state.finish()
#     await message.reply('Ну ладно')
#
#
# @dp.message_handler(state=FSMAdmin.mentor_username)
# async def append_mentor_username(message: types.Message, state: FSMContext):
#     if message.from_user.id in overlords:
#         async with state.proxy() as data:
#             data['mentor_name'] = message.text[1:]
#         admins.append(data['mentor_name'])
#         await message.reply('Обучатор добавлен')
#         await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'])
    dp.register_message_handler(cm_start, lambda message: message.text.startswith('Загрузить'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=FSMAdmin.document)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_callback_query_handler(load_form, lambda x: x.data and x.data.startswith('С'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, lambda x: x.data and x.data.startswith('Аттестация'),
                                       state=FSMAdmin.status)
    dp.register_message_handler(load_link, state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    dp.register_message_handler(start_search, lambda message: message.text.startswith('Найти'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(search_item, state=FSMAdmin.trainee_name)
