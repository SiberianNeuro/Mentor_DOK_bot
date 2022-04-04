from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_load = KeyboardButton('/Загрузить')
button_delete = KeyboardButton('/Удалить')
button_search = KeyboardButton('/Найти')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load).add(button_delete).add(button_search)