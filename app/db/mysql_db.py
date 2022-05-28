import pymysql.cursors
import logging

from app.services.config import load_config


async def mysql_start():
    global conn
    config = load_config()
    conn = pymysql.connect(
            host=config.db.host,
            user=config.db.user,
            password=config.db.password,
            database=config.db.database,
            cursorclass=pymysql.cursors.Cursor,
            charset='utf8mb4',
        )
    if conn:
        logging.info('Database connected.')

# def sql_start():
#     global base, cur
#     base = sq.connect('mentor_base.db')
#     cur = base.cursor()
#     if base:
#         logging.info('Database connected')
#     base.execute('CREATE TABLE IF NOT EXISTS at_list(document TEXT, '
#                  'name TEXT, format TEXT, status TEXT, link TEXT, '
#                  'date DATE, exam_id INTEGER PRIMARY KEY)')
#     base.execute('CREATE TABLE IF NOT EXISTS staff_DOK(name TEXT, position TEXT, username TEXT, chat_id INT, '
#                  'reg_time TEXT)')
#     base.commit()


"""Запросы от администратора"""


# Добавить опрос в БД
async def sql_add_command(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO exam_results (document_id, fullname, exam_format, exam_status, exam_YT_link, exam_date) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


# Найти опрос по айдишнику документа
async def item_search(data):
    with conn.cursor() as cur:
        sql = "SELECT * FROM exam_results WHERE document_id = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
    return result
    # return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

# Найти все опросы по ФИО стажера
async def name_search(data):
    with conn.cursor() as cur:
        sql = "SELECT * FROM exam_results WHERE fullname LIKE %s"
        cur.execute(sql, ('%' + data + '%',))
        result = cur.fetchall()
    return result

# Удалить запись об опросе
async def sql_delete_command(data):
    with conn.cursor() as cur:
        sql = "DELETE FROM exam_results WHERE idexam_results = %s"
        cur.execute(sql, (data,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def chat_id_check():
    with conn.cursor() as cur:
        sql = "SELECT chat_id FROM DOK_users"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def add_user(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO DOK_users (fullname, pos, username, chat_id, reg_date) VALUES (%s, %s, %s, %s, CURRENT_DATE)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()