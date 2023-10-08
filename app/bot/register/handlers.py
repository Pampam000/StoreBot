from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot import crud
from app.bot.register.states import Register

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    messages, _, __ = \
        await crud.get_state_messages(state_name='Register:start',
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    await state.set_state(Register.enter_password)
    await state.update_data(count=0)

    await message.answer(messages[0]['text'])


@router.message(F.text, Register.enter_password)
async def enter_password(message: Message, state: FSMContext):
    password: str = message.text
    state_name: str = await state.get_state()

    messages, _, __ = \
        await crud.get_state_messages(state_name=state_name,
                                      with_inline_kb=False,
                                      with_reply_kb=False)

    messages = {msg['name']: msg['text'] for msg in messages}

    if password != '1234':
        data = await state.get_data()
        count = data['count'] + 1

        if count == 3:
            await state.clear()
            await message.answer(messages['incorrect_password_3_times'])
            return

        await state.update_data(count=count)
        await message.answer(messages['incorrect_paasword'])
        return

    await message.answer(messages['correct_password'])
    await state.clear()
