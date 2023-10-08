from aiogram.fsm.state import StatesGroup, State


class Register(StatesGroup):
    enter_password = State()
