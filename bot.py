import logging

from aiogram.utils import executor

from app.utils.misc.set_bot_commands import set_default_commands
from app.utils.notify_admins import on_startup_notify
from loader import dp

from app.db import sqlite_db
from app.handlers.users import admin, other, overlord, trainee


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO,
                        # level=logging.DEBUG,  # Можно заменить на другой уровень логгирования.
                        )
    sqlite_db.sql_start()


trainee.register_handlers_trainee(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)
overlord.register_handlers_overlord(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)