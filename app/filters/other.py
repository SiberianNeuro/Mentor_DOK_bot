from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.db.mysql_db import chat_id_check


async def is_register(obj):
    result = await chat_id_check()
    if obj not in result:
        return False
    else:
        return True