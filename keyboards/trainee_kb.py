from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Режим работы')
# b2 = KeyboardButton('Расположение')
# b3 = KeyboardButton('Меню')

kb_trainee = ReplyKeyboardMarkup

kb_trainee.add(b1)