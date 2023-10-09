from aiogram.fsm.state import StatesGroup, State


class Register(StatesGroup):
    enter_password = State()
    choose_option = State()
    enter_referral_code = State()
    enter_location = State()
    country = State()
    federal_region = State()
    region = State()
    city = State()

