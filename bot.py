from aiogram.utils import executor

from app.utils.misc.set_bot_commands import set_default_commands
from app.utils.notify_admins import on_startup_notify
from loader import dp

from app.db import sqlite_db
from app.handlers.users import admin, other, overlord, trainee
from app.filters.admin import AdminFilter


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    sqlite_db.sql_start()

def register_all
trainee.register_handlers_trainee(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)
overlord.register_handlers_overlord(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)