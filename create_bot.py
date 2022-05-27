from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

storage = MemoryStorage()
bot = Bot(token='5273904306:AAG_oagNyzM2nwmajGcPHERGfyvtD5XLUMc', parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)