import logging
import sqlite3 as sq
import logging


def sql_start():
    global base, cur
    base = sq.connect('mentor_base.db')
    cur = base.cursor()
    if base:
        logging.info('Database connected')
    base.execute('CREATE TABLE IF NOT EXISTS at_list(document TEXT, '
                 'name TEXT, format TEXT, status TEXT, link TEXT, '
                 'date DATE, exam_id INTEGER PRIMARY KEY)')
    base.execute('CREATE TABLE IF NOT EXISTS admins(chat_id TEXT, username TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS staff_DOK(name TEXT, position TEXT, username TEXT, chat_id INT, '
                 'reg_time TEXT)')
    base.commit()

async def sql_staff_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO staff_DOK VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_staff_chat_id_read():
    return cur.execute('SELECT chat_id FROM staff_DOK').fetchall()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO at_list (document, name, format, status, link, date) VALUES (?, ?, ?, ?, ?, ?)',
                    tuple(data.values()))
        base.commit()







async def item_search():
    return cur.execute('SELECT * FROM at_list').fetchall()


async def sql_search_command(data):
    return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

async def sql_delete_command(data):
    cur.execute('DELETE FROM at_list WHERE exam_id == ?', (data,))
    base.commit()