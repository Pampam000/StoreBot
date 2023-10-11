from aiogram.fsm.state import StatesGroup, State


class Register(StatesGroup):
    password = State()
    choose_option = State()
    referral_code = State()


class Location(StatesGroup):
    country = State()
    federal_region = State()
    region = State()
    city = State()
    district = State()
    micro_district = State()
