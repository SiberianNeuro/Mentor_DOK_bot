import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

async def on_startup(_):
    print('Бот вышел в онлайн')
"""Стажеры"""

@dp.message_handler(commands=['start', 'help'])
async def commands_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'К Вашим услугам')
        await message.delete()
    except:
        await message.reply('Общение со мной возможно только в личке:\nhttps://t.me/Mentor_DOK_bot')
@dp.message_handler(commands=['Режим работы'])
async def bot_open_command(message : types.Message):
    await message.reply('В процессе разработки')
"""Наставники"""

"""Остальное"""


@dp.message_handler()
async def echo_send(message : types.Message):
    if message.text == 'Привет':
        await message.answer('И тебе привет')
    # await message.answer(message.text)
    # await message.reply(message.text)
    # await bot.send_message(message.from_user.id, message.text)




executor.start_polling(dp, skip_updates=True, on_startup=on_startup)