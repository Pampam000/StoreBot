from fastapi import APIRouter, HTTPException, Body, Path

from app.bot import crud as bot_crud
from . import crud
from .schemas import MessageSchema, ButtonSchema, AddMessageSchema, \
    UpdateMessageText, UpdateButton
from .schemas import UpdateOrder

router = APIRouter(prefix='/messages',
                   tags=['messages'])

buttons_router = APIRouter(tags=['buttons'])


@router.get('/states')
async def get_states():
    return await crud.get_states()


@router.get('/')
async def get_messages(state_name: str):
    messages, inline_kbs, __ = \
        await bot_crud.get_state_messages(state_name=state_name,
                                          with_inline_kb=True,
                                          with_reply_kb=False)

    messages = list(map(lambda m: MessageSchema(**m), messages))
    for message in messages:
        for message_id in inline_kbs:
            if message.id != message_id:
                continue
            buttons = [ButtonSchema(**x) for x in inline_kbs[message_id]]
            message.callback_buttons = buttons

    return messages


@router.post('/{message_group_id}')
async def add_message(message_group_id: int = Path(..., ge=1),
                      message: AddMessageSchema = Body(...)):
    await crud.add_message(message=message, message_group_id=message_group_id)
    return message


@router.patch('/{message_id}')
async def update_message_text(message_id: int = Path(..., ge=1),
                              text: UpdateMessageText = Body(...)):
    return await crud.update_message_text(message_id=message_id,
                                          text=text.text)


@router.patch('/{message_group_id}')
async def update_message_order(message_group_id: int = Path(..., ge=1),
                               order: UpdateOrder = Body(...)):
    order.order = sorted(order.order, key=lambda o: o.message_id)
    await crud.update_order(order=order, message_group_id=message_group_id)


@router.delete('/{message_id}', status_code=204)
async def delete_message(message_id: int = Path(..., ge=1)):
    if detail := await crud.delete_message(message_id=message_id):
        raise HTTPException(status_code=400, detail=detail)


@buttons_router.get('/messages/{message_id}/buttons')
async def get_message_buttons(message_id: int = Path(..., ge=1)):
    return await crud.get_message_buttons(message_id=message_id)


@buttons_router.patch('/buttons/{button_id}')
async def update_button(button_id: int = Path(..., ge=1),
                        text: UpdateButton = Body(...)):
    return await crud.update_button(button_id=button_id,
                                    text=text.text)


# @buttons_router.get('/keyboards{keyboard_id}')
# async def get_menu_buttons(keyboard_id: int = Path(..., ge=1)):
@buttons_router.get('/buttons')
async def get_menu_buttons(state_name: str):
    return await crud.get_menu_buttons(state_name=state_name)
