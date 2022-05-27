import logging

from aiogram import Dispatcher

from app.services.config import load_config

config = load_config()

async def on_startup_notify(dp: Dispatcher):
    for admin in config.tg_bot.admin_ids:
        try:
            await dp.bot.send_message(admin, "Бот запущен")

        except Exception as err:
            logging.exception(err)