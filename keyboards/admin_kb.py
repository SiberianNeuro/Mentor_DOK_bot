from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

button_load = KeyboardButton('Загрузить')
button_cancel = KeyboardButton('Отмена')
button_search = KeyboardButton('Найти')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button_load, button_search)
button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(button_cancel)

button_trainee_L3 = InlineKeyboardButton('🟡 На И.О.', callback_data='Со стажера на И.О.')
button_doc_L3 = InlineKeyboardButton('🔴 На врача', callback_data='С И.О. на врача')
button_trainee_L1 = InlineKeyboardButton('🟢 Аттестация помощника', callback_data='Со стажера L1 на сотрудника')
button_stage_full = InlineKeyboardMarkup(row_width=2).row(button_trainee_L3, button_doc_L3)
button_stage_full.add(button_trainee_L1)

button_success = InlineKeyboardButton('😏 Прошел', callback_data='Аттестация пройдена ✅')
button_fault = InlineKeyboardButton('😒 Не прошел', callback_data='Аттестация не пройдена ❌')
button_outcome_full = InlineKeyboardMarkup(row_width=2).row(button_success, button_fault)
