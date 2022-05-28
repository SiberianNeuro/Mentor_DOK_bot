from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.services.config import load_config


class RegFilter(BoundFilter):
    async def check(self, obj):
