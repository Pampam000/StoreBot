import aiohttp
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

    # delete_list: list[Message | SendMessage] = \
    #    await add_messages_to_delete_list(user_message=message,
    # bot_messages=messages)

    for msg in messages:
        await message.answer(msg['text'])

    await state.update_data(count=0)


@router.message(F.text, Register.password)
async def enter_password(message: Message, state: FSMContext):
    password: str = message.text
    state_name: str = await state.get_state()

    messages, inline_kbs, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=True,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['incorrect', 'incorrect_3_times', 'correct'])

    if await check_password(password=password,
                            message=message,
                            messages=messages, state=state):
        return

    for num, msg in enumerate(messages['correct']):
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)

        m = await message.answer(msg['text'], reply_markup=kb)
        # data['delete_list'].append(m)
    # data['delete_list'].append(message)
    await state.set_state(Register.choose_option)


@router.callback_query(Register.choose_option, F.data == 'referral code')
async def begin_enter_referral_code(callback: CallbackQuery,
                                    state: FSMContext):
    # data = await state.get_data()

    state_name: str = await state.get_state()
    state_name += ':referral_code'
    messages, _, reply_kbs = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    for msg in messages:
        m = await callback.message.answer(msg['text'])
        # data['delete_list'].append(m)

    # print(222222)
    # print([x.text for x in data['delete_list']])
    # await state.update_data(delete_list=data['delete_list'])
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

        m = await message.answer(msg['text'], reply_markup=kb)
        # data['delete_list'].append(m)
    # data['delete_list'].append(message)
    # print(333333)
    # print([x.text for x in data['delete_list']])
    # await state.update_data(delete_list=data['delete_list'])
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

    # async with aiohttp.ClientSession() as session:
    #    async with session.get(
    #            'https://iqpr.cc/api/v1/locality_list/COUNTRY') as response:
    #        response = await response.json()
    #
    # data = {}
    # for country in response['data']:
    #    data[country['id']] = country['title']

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
    await _save(message=message, state=state)


async def _save(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        data = await state.get_data()
        print(data)
        response = await session.patch(
            'https://iqpr.cc/api/v1/update_user_data/3/',
            data=data)
        print(response.status)

    await state.clear()


@router.message(Location.country, F.text)
async def enter_country(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)

    state_name = await state.get_state()
    if not await check(state_name=state_name,
                       message=message,
                       location='COUNTRY'):
        await state.set_state(Location.federal_region)


@router.message(Location.federal_region, F.text)
async def enter_federal_region(message: Message, state: FSMContext):
    federal_region = message.text
    await state.update_data(federal_region=federal_region)

    state_name = await state.get_state()

    if not await check(state_name=state_name,
                       message=message,
                       location='FEDERAL_REGION'):
        await state.set_state(Location.region)


@router.message(Location.region, F.text)
async def enter_region(message: Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    state_name = await state.get_state()

    if not await check(state_name=state_name,
                       message=message,
                       location='REGION'):
        await state.set_state(Location.city)


@router.message(Location.city, F.text)
async def enter_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)

    state_name = await state.get_state()

    if not await check(state_name=state_name,
                       message=message,
                       location='CITY'):
        await state.set_state(Location.district)


@router.message(Location.district, F.text)
async def enter_district(message: Message, state: FSMContext):
    district = message.text
    await state.update_data(district=district)

    state_name = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['not_found', 'correct'])

    for msg in messages['correct']:
        await message.answer(msg['text'])

    await state.set_state(Location.micro_district)


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
    await _save(message=message, state=state)


@router.callback_query(F.data == 'to catalog')
async def to_catalog(callback: CallbackQuery, state: FSMContext):
    # await delete_messages(state=state)
    await callback.message.answer('В каталоге')
    await callback.answer()
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
    print([x.text for x in messages])
    for num, m in enumerate(messages):
        # if num <= len(messages) - 1:
        await m.delete()

    await state.set_data({})


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
                         message: Message) -> int:
    if password != '1234':
        data = await state.get_data()
        count = data['count'] + 1

        if count == 3:

            for msg in messages['incorrect_3_times']:
                await message.answer(msg['text'])
            await state.update_data(count=0)
            await state.set_state(None)
            return True

        for msg in messages['incorrect']:
            await message.answer(msg['text'])
            await state.update_data(count=count)
        return True


async def check_referral_code(code: str,
                              messages: dict,
                              message: Message) -> bool:
    if code != '5678':

        if code == '5555':
            for msg in messages['used']:
                await message.answer(msg['text'])
            return True

        for msg in messages['incorrect']:
            await message.answer(msg['text'])
        return True


async def check(state_name: str,
                message: Message,
                location: str):
    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['not_found', 'correct'])

    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://iqpr.cc/api/v1/locality_list/{location}') as response:
            response = await response.json()

    titles = [x['title'] for x in response['data']]

    if message.text not in titles:
        for msg in messages['not_found']:
            await message.answer(msg['text'])
        return True

    for msg in messages['correct']:
        await message.answer(msg['text'])
