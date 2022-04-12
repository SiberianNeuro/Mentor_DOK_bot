import sqlite3 as sq
from create_bot import bot

def sql_start():
    global base, cur
    base = sq.connect('mentor_base.db')
    cur = base.cursor()
    if base:
        print('Data base connected.')
    base.execute('CREATE TABLE IF NOT EXISTS at_list(document TEXT, name TEXT, format TEXT, status TEXT, price TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS admins(chat_id TEXT username TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS staff(chat_id TEXT username TEXT name TEXT pos TEXT)')
    base.commit()

async def sql_staff_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO staff VALUES (?, ?, ?, ?)', tuple(data.values()))

async def sql_staff_chat_id_read():
    return cur.execute('SELECT chat_id FROM staff').fetchall()

async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO at_list VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_read(message):
    for ret in cur.execute('SELECT * FROM at_list WHERE document == ?', (ret[0],)).fetchone():
        await bot.send_message(message.from_user.id, f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[-1]}')
        await bot.send_document(message.from_user.id, ret[0])

async def sql_read2():
    return cur.execute('SELECT * FROM at_list').fetchall()

async def sql_search_command(data):
    return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

async def sql_delete_command(data):
    cur.execute('DELETE FROM at_list WHERE name == ?', (data,))
    base.commit()