from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_trainee

# @dp.message_handler(commands=['start', 'help'])
async def commands_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'К Вашим услугам', reply_markup=kb_trainee)
        await message.delete()
    except:
        await message.reply('Общение со мной возможно только в личке:\nhttps://t.me/Mentor_DOK_bot')
# @dp.message_handler(commands=['Режим работы'])
async def bot_open_command(message : types.Message):
    await message.reply('В процессе разработки')

def register_handlers_trainee(dp : Dispatcher):
    dp.register_message_handler(commands_start, commands=['start', 'help'])
    dp.register_message_handler(bot_open_command, commands=['Режим работы'])
    # dp.register_message_handler()