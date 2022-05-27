from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()
    date = State()
    trainee_name = State()
    mentor_username = State()