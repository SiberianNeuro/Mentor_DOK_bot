from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

storage = MemoryStorage()
bot = Bot(token='5272216108:AAEAdG72QfeB95dwcGLliF_Cv_X_Ou0ZU44', parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)