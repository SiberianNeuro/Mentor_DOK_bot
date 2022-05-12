import sqlite3 as sq
from create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import admin_kb

def sql_start():
    global base, cur
    base = sq.connect('mentor_base.db')
    cur = base.cursor()
    if base:
        print('Data base connected.')
    base.execute('CREATE TABLE IF NOT EXISTS at_list(document TEXT, name TEXT, format TEXT, status TEXT, price TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS admins(chat_id TEXT, username TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS staff_DOK(name TEXT, position TEXT, username TEXT, chat_id INT, reg_time TEXT)')
    base.commit()

async def sql_staff_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO staff_DOK VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_staff_chat_id_read():
    return cur.execute('SELECT chat_id FROM staff_DOK').fetchall()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO at_list VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_read(message):
    for ret in cur.execute('SELECT * FROM at_list WHERE document == ?', (ret[0],)).fetchone():
        await bot.send_message(message.from_user.id, f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}')
        await bot.send_document(message.from_user.id, ret[0])



async def item_search():
    return cur.execute('SELECT * FROM at_list').fetchall()


async def sql_search_command(data):
    return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

async def sql_delete_command(data):
    cur.execute('DELETE FROM at_list WHERE exam_id == ?', (data,))
    base.commit()

async def sql_report_trainee(date_1, date_2):
    return cur.execute(f'SELECT name FROM at_list WHERE date BETWEEN "{date_1}" AND "{date_2}"'
                       f'AND format == "Со стажера на И.О."')


async def sql_report_l1(date_1, date_2):
    return cur.execute(f'SELECT name FROM at_list WHERE date BETWEEN "{date_1}" AND "{date_2}"'
                       f'AND format == "Со стажера L1 на сотрудника"')


async def sql_report_doc(date_1, date_2):
    return cur.execute(f'SELECT name FROM at_list WHERE date BETWEEN "{date_1}" AND "{date_2}"'
                       f'AND format == "С И.О. на врача"')