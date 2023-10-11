from aiogram import Router, F
from aiogram.filters import CommandStart, Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message, CallbackQuery
from asyncpg import Record

from app.bot import crud, keyboards
from app.bot.register.states import Register, Location

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    messages, _, __ = \
        await crud.get_state_messages(state_name='Register:start',
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    await state.set_state(Register.password)

    delete_list: list[Message | SendMessage] = \
        await add_messages_to_delete_list(user_message=message,
                                          bot_messages=messages)

    await state.update_data(count=0, delete_list=delete_list)


@router.message(F.text, Register.password)
async def enter_password(message: Message, state: FSMContext):
    await delete_messages(state=state)

    password: str = message.text
    state_name: str = await state.get_state()

    messages, inline_kbs, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=True,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['incorrect', 'incorrect_3_times', 'correct'])

    if await check_password(password=password, message=message,
                            messages=messages, state=state):
        return

    for num, msg in enumerate(messages['correct']):
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)

        await message.answer(msg['text'], reply_markup=kb)

    await state.set_state(Register.choose_option)


@router.callback_query(Register.choose_option, F.data == 'referral code')
async def begin_enter_referral_code(callback: CallbackQuery,
                                    state: FSMContext):
    state_name: str = await state.get_state()
    state_name += ':referral_code'
    messages, _, reply_kbs = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await callback.message.answer(msg['text'])

    await state.set_state(Register.referral_code)
    await callback.answer()


@router.message(Register.referral_code, F.text)
async def enter_referral_code(message: Message, state: FSMContext):
    code: str = message.text

    state_name: str = await state.get_state()

    messages, inline_kbs, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=True,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['incorrect', 'used', 'correct'])

    if await check_referral_code(code=code, messages=messages,
                                 message=message):
        return

    for num, msg in enumerate(messages['correct']):
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)

        await message.answer(msg['text'], reply_markup=kb)

    await state.clear()


@router.callback_query(Register.choose_option, F.data == 'location')
async def begin_enter_locality(callback: CallbackQuery, state: FSMContext):
    await state.set_data({})
    await state.set_state(Location.country)
    state_name = 'Location:start'

    messages, _, reply_buttons = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=True)

    for num, msg in enumerate(messages):
        kb = None
        if num == 0:
            buttons: list[str] = [x['text'] for x in reply_buttons]
            kb = keyboards.create_reply_keyboard(buttons=buttons)

        await callback.message.answer(msg['text'], reply_markup=kb)

    await callback.answer()


class ButtonFilter(Filter):
    def __init__(self, button: str):
        self.button = button

    async def __call__(self, message: Message) -> bool:
        text: str = await crud.get_menu_button_by_name(name=self.button)
        return message.text == text


@router.message(ButtonFilter('save'), StateFilter(Location))
async def save(message: Message, state: FSMContext):
    await state.clear()


@router.message(Location.country, F.text)
async def enter_country(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)

    state_name = await state.get_state()
    await state.set_state(Location.federal_region)
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await message.answer(msg['text'])


@router.message(Location.federal_region, F.text)
async def enter_federal_region(message: Message, state: FSMContext):
    federal_region = message.text
    await state.update_data(federal_region=federal_region)

    state_name = await state.get_state()
    await state.set_state(Location.region)
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await message.answer(msg['text'])


@router.message(Location.region, F.text)
async def enter_region(message: Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    state_name = await state.get_state()
    await state.set_state(Location.city)
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await message.answer(msg['text'])


@router.message(Location.city, F.text)
async def enter_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)

    state_name = await state.get_state()
    await state.set_state(Location.district)
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await message.answer(msg['text'])


@router.message(Location.district, F.text)
async def enter_district(message: Message, state: FSMContext):
    district = message.text
    await state.update_data(district=district)

    state_name = await state.get_state()
    await state.set_state(Location.micro_district)
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    for msg in messages:
        await message.answer(msg['text'])


@router.message(Location.micro_district, F.text)
async def enter_micro_district(message: Message, state: FSMContext):
    micro_district = message.text

    await state.update_data(micro_district=micro_district)

    state_name = await state.get_state()
    state_name += ':success'

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    for msg in messages:
        await message.answer(msg['text'])

    # await message.answer(str(await state.get_data()))
    await state.clear()


@router.callback_query(F.data == 'to catalog')
async def to_catalog(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Логика не прописана', show_alert=True)
    await state.clear()


async def add_messages_to_delete_list(
        user_message: Message,
        bot_messages: list[SendMessage]) -> list[Message | SendMessage]:
    delete_list = [user_message]
    for msg in bot_messages:
        sent_message: SendMessage = await user_message.answer(msg['text'])
        delete_list.append(sent_message)

    return delete_list


async def delete_messages(state: FSMContext):
    data = await state.get_data()
    messages: list[Message | SendMessage] = data['delete_list']

    for num, m in enumerate(messages.copy()):
        if num <= len(messages) - 1:
            await m.delete()
            messages.remove(m)

    await state.update_data(delete_list=messages)


def get_message_cases(messages: list[Record],
                      keys: list[str]) -> dict[str, list]:
    lists = [[] for _ in range(len(keys))]
    current_priority = 0
    count = 0
    current_list = lists[count]

    for message in messages:
        if message['priority'] <= current_priority:
            count += 1
            current_list = lists[count]

        current_list.append(message)
        current_priority = message['priority']

    messages = {x: y for x, y in
                zip(keys, lists)}

    return messages


async def check_password(password: str,
                         state: FSMContext,
                         messages: dict,
                         message: Message):
    if password != '1234':
        data = await state.get_data()
        count = data['count'] + 1

        if count == 3:
            await state.clear()
            for msg in messages['incorrect_3_times']:
                await message.answer(msg['text'])
            return True

        await state.update_data(count=count)
        for msg in messages['incorrect']:
            await message.answer(msg['text'])
        return True


async def check_referral_code(code: str,
                              messages: dict,
                              message: Message):
    if code != '5678':

        if code == '5555':
            for msg in messages['used']:
                await message.answer(msg['text'])
            return True

        for msg in messages['incorrect']:
            await message.answer(msg['text'])
        return True
