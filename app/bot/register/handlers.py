import aiohttp
from aiogram import Router, F
from aiogram.filters import CommandStart, Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message, CallbackQuery
from asyncpg import Record

from app import main_backend
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

    delete_list = [message]
    for msg in messages:
        m = await message.answer(msg['text'])
        delete_list.append(m)

    await state.update_data(count=0, delete_list=delete_list, locations=[])


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

    data = await state.get_data()
    data['delete_list'].append(message)
    for num, msg in enumerate(messages['correct']):
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)

        m = await message.answer(msg['text'], reply_markup=kb)
        data['delete_list'].append(m)

    await state.update_data(delete_list=data['delete_list'])
    await delete_messages(state, count=len(messages['correct']))
    await state.set_state(Register.choose_option)


@router.callback_query(Register.choose_option, F.data == 'referral code')
async def begin_enter_referral_code(callback: CallbackQuery,
                                    state: FSMContext):
    data = await state.get_data()
    print(data.keys())
    state_name: str = await state.get_state()
    state_name += ':referral_code'
    messages, _, reply_kbs = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    for msg in messages:
        m = await callback.message.answer(msg['text'])
        data['delete_list'].append(m)

    print(222222)
    print([x.text for x in data['delete_list']])
    await state.update_data(delete_list=data['delete_list'])
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
                                 message=message, state=state):
        return

    data = await state.get_data()
    data['delete_list'].append(message)
    for num, msg in enumerate(messages['correct']):
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)

        m = await message.answer(msg['text'], reply_markup=kb)
        data['delete_list'].append(m)

    print(333333)
    print([x.text for x in data['delete_list']])
    # await state.update_data(delete_list=data['delete_list'])
    await delete_messages(state, len(messages['correct']))
    await state.clear()


@router.callback_query(Register.choose_option, F.data == 'location')
async def begin_enter_locality(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Location.country)
    state_name = 'Location:start'

    messages, _, reply_buttons = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=True)

    locations = await main_backend.get_location_list(location="COUNTRY")
    data = {}

    print(messages)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['inline', 'base'])

    print(messages)
    for country in locations['data']:
        data[str(country['id'])] = country['title']

    print(data)

    inline_kb = keyboards.create_inline_keyboard(buttons=data.values(),
                                                 callbacks=data.keys())

    print(inline_kb)
    data = await state.get_data()
    for num, msg in enumerate(messages['inline']):
        kb = None
        if num == len(messages['inline']) - 1:
            kb = inline_kb

        m = await callback.message.answer(msg['text'], reply_markup=kb)
        data['delete_list'].append(m)

    for num, msg in enumerate(messages['base']):

        kb = None

        if num == 0:
            buttons: list[str] = [x['text'] for x in reply_buttons]
            kb = keyboards.create_reply_keyboard(buttons=buttons)

        m = await callback.message.answer(msg['text'], reply_markup=kb)
        data['delete_list'].append(m)
    await state.update_data(locations=locations,
                            delete_list=data['delete_list'])

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

    await delete_messages(state, 1)
    await state.clear()


@router.message(Location.country, F.text)
async def enter_country(message: Message, state: FSMContext):
    country = message.text
    await state.update_data(country=country)
    data = await state.get_data()

    if not await check(message=message, state=state):
        await state.set_state(Location.federal_region)


@router.callback_query(Location.country)
async def enter_country_callback(callback: CallbackQuery, state: FSMContext):
    country_id = callback.data
    await state.update_data(country_id=country_id)
    await check(message=callback.message,
                state=state,
                callback_data=callback.data)
    await state.set_state(Location.federal_region)
    await callback.answer()


@router.message(Location.federal_region, F.text)
async def enter_federal_region(message: Message, state: FSMContext):
    federal_region = message.text
    await state.update_data(federal_region=federal_region)
    if not await check(message=message, state=state):
        await state.set_state(Location.region)


@router.callback_query(Location.federal_region)
async def enter_federal_region_callback(callback: CallbackQuery,
                                        state: FSMContext):
    federal_region_id = callback.data
    await state.update_data(federal_region_id=federal_region_id)
    await check(message=callback.message,
                state=state,
                callback_data=callback.data)
    await state.set_state(Location.region)
    await callback.answer()


@router.message(Location.region, F.text)
async def enter_region(message: Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)
    if not await check(message=message, state=state):
        await state.set_state(Location.city)


@router.callback_query(Location.region)
async def enter_region_callback(callback: CallbackQuery, state: FSMContext):
    region_id = callback.data
    await state.update_data(region_id=region_id)
    await check(message=callback.message,
                state=state,
                callback_data=callback.data)
    await state.set_state(Location.city)
    await callback.answer()


@router.message(Location.city, F.text)
async def enter_city(message: Message, state: FSMContext):
    city = message.text
    data = await state.get_data()

    await state.update_data(city=city)
    state_name = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['not_found', 'inline', 'correct'])

    state_data = await state.get_data()
    locations = state_data['locations']

    titles = []

    for location in locations['data']:
        titles.append(location['title'])

    data['delete_list'].append(message)
    if message.text not in titles:
        for msg in messages['not_found']:
            m = await message.answer(msg['text'])
            data['delete_list'].append(m)

        return True

    for msg in messages['inline']:
        m = await message.answer(msg['text'])
        data['delete_list'].append(m)

    await state.update_data(delete_list=data['delete_list'])
    await state.set_state(Location.district)


@router.callback_query(Location.city)
async def enter_city_callback(callback: CallbackQuery, state: FSMContext):
    city_id = callback.data
    await state.update_data(city_id=city_id)
    data = await state.get_data()

    state_name = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)
    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['not_found', 'inline', 'correct'])

    state_data = await state.get_data()
    locations = state_data['locations']

    titles = []

    for location in locations['data']:
        titles.append(location['title'])

    for msg in messages['inline']:
        m = await callback.message.answer(msg['text'])
        data['delete_list'].append(m)

    await state.update_data(delete_list=data['delete_list'])
    await state.set_state(Location.district)
    data = await state.get_data()
    print(111111111, data)
    await callback.answer()


@router.message(Location.district, F.text)
async def enter_district(message: Message, state: FSMContext):
    district = message.text
    await state.update_data(district=district)
    data = await state.get_data()
    state_name = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['inline', 'correct'])

    data['delete_list'].append(message)
    for msg in messages['inline']:
        m = await message.answer(msg['text'])
        data['delete_list'].append(m)

    await state.update_data(delete_list=data['delete_list'])
    await state.set_state(Location.micro_district)


@router.message(Location.micro_district, F.text)
async def enter_micro_district(message: Message, state: FSMContext):
    micro_district = message.text
    data = await state.get_data()
    await state.update_data(micro_district=micro_district)

    state_name = await state.get_state()
    state_name += ':success'

    messages, inline_kbs, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=True,
                                      with_reply_kb=False)

    data['delete_list'].append(message)
    for msg in messages:
        kb = None
        if msg['id'] in inline_kbs:
            buttons: list[str] = [x['text'] for x in inline_kbs[msg['id']]]
            kb = keyboards.create_inline_keyboard(buttons=buttons)
        m = await message.answer(msg['text'], reply_markup=kb)
        data['delete_list'].append(m)
    await state.update_data(delete_list=data['delete_list'])
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


async def delete_messages(state: FSMContext, count: int):
    data = await state.get_data()
    messages: list[Message | SendMessage] = data['delete_list']

    print(count)
    print(len(messages))
    print([x.text for x in messages])
    messages_to_remove = []
    for num, m in enumerate(messages.copy()):

        if num + count + 1 > len(messages):
            break
        print(m.text)
        await m.delete()
        messages_to_remove.append(m)

    for m in messages_to_remove:
        messages.remove(m)

    print(10101010110101010101, [x.text for x in messages])
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
                         message: Message) -> int:
    state_data = await state.get_data()
    delete_list = state_data['delete_list']

    if password != '1234':
        delete_list.append(message)
        data = await state.get_data()
        count = data['count'] + 1

        if count == 3:

            for msg in messages['incorrect_3_times']:
                m = await message.answer(msg['text'])
                delete_list.append(m)

            await state.update_data(count=0, delete_list=delete_list)
            await state.set_state(None)
            data = await state.get_data()
            delete_list = data['delete_list']

            await delete_messages(state, 1)
            return True

        for msg in messages['incorrect']:
            m = await message.answer(msg['text'])
            delete_list.append(m)
            await state.update_data(count=count, delete_list=delete_list)
        return True


async def check_referral_code(code: str,
                              messages: dict,
                              state: FSMContext,
                              message: Message) -> bool:
    state_data = await state.get_data()
    delete_list = state_data['delete_list']
    if code != '5678':
        delete_list.append(message)
        if code == '5555':
            for msg in messages['used']:
                m = await message.answer(msg['text'])
                delete_list.append(m)
            print('aaaaaaaaaaaaaaaaaaaaaaaaaa', [x.text for x in delete_list])
            await state.update_data(delete_list=delete_list)
            return True

        for msg in messages['incorrect']:
            m = await message.answer(msg['text'])
            delete_list.append(m)
        print('bbbbb', [x.text for x in delete_list])
        await state.update_data(delete_list=delete_list)
        return True


async def check(message: Message, state: FSMContext,
                callback_data=None):
    state_name = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    messages: dict[str, list] = get_message_cases(
        messages=messages,
        keys=['not_found', 'inline', 'correct'])

    state_data = await state.get_data()
    locations = state_data['locations']

    titles = []
    ids = []
    for location in locations['data']:
        titles.append(location['title'])
        ids.append(location['id'])
    location = locations['data'][0]['locality']

    if not callback_data:
        state_data['delete_list'].append(message)
        if message.text not in titles:
            for msg in messages['not_found']:
                m = await message.answer(msg['text'])
                state_data['delete_list'].append(m)
            return True

        index = titles.index(message.text)
        parent_id = ids[index]
    else:
        parent_id = callback_data
    locations = await main_backend.get_locations_with_parent(
        location=location,
        parent_id=parent_id)
    data = {}

    for location in locations['data']:
        data[str(location['id'])] = location['title']

    print(data)

    inline_kb = keyboards.create_inline_keyboard(buttons=data.values(),
                                                 callbacks=data.keys())

    for num, msg in enumerate(messages['inline']):
        kb = None
        if num == len(messages['inline']) - 1:
            kb = inline_kb

        m = await message.answer(msg['text'], reply_markup=kb)
        state_data['delete_list'].append(m)
    for num, msg in enumerate(messages['correct']):
        m = await message.answer(msg['text'])
        state_data['delete_list'].append(m)
    await state.update_data(locations=locations,
                            delete_list=state_data['delete_list'])
