from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


trainee_button = InlineKeyboardButton('Стажер', callback_data='Стажер врача')
junior_button = InlineKeyboardButton('ИО врача', callback_data='И.О. врача')
middle_button = InlineKeyboardButton('Врач', callback_data='Врач')

pos_case_button = InlineKeyboardMarkup(row_width=2).row(trainee_button, junior_button)
pos_case_button.add(middle_button)