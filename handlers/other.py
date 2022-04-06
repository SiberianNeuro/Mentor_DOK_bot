from aiogram import types, Dispatcher
from create_bot import dp, bot



# @dp.message_handler()
async def echo_send(message : types.Message):
    if message.text == 'Привет':
        a = message.from_user.username
        await message.answer('И тебе привет')
        await bot.send_message(message.from_user.id, f'@{a}')
    # await message.answer(message.text)
    # await message.reply(message.text)
    # await bot.send_message(message.from_user.id, message.text)

def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)