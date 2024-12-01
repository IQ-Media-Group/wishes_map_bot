from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    tg_id = State()
    name = State()
    email = State()
    phone = State()