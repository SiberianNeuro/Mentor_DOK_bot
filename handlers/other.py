from aiogram import types
from create_bot import dp


@dp.message_handler()
async def echo_send(message : types.Message):
    if message.text == 'Привет':
        await message.answer('И тебе привет')
    # await message.answer(message.text)
    # await message.reply(message.text)
    # await bot.send_message(message.from_user.id, message.text)