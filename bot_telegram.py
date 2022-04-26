from aiogram.utils import executor
from create_bot import dp
from db import sqlite_db
from handlers import trainee, admin, other, overlord
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def on_startup(_):
    print('Бот вышел в онлайн')
    sqlite_db.sql_start()


trainee.register_handlers_trainee(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)
overlord.register_handlers_overlord(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)