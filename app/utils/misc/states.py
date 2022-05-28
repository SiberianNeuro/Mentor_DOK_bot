from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    document = State()
    name = State()
    form = State()
    status = State()
    link = State()
    trainee_name = State()
    mentor_username = State()


class FSMRegister(StatesGroup):
    chat_id = State()
    name = State()
    username = State()
    position = State()
    reg_time = State()