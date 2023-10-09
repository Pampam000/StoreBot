from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_inline_keyboard(
        buttons: list[str],
        callbacks: list[str] = None) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    if callbacks:
        if len(buttons) != len(callbacks):
            raise
    else:
        callbacks = buttons


    for button, callback in zip(buttons, callbacks):
        builder.button(text=button, callback_data=callback)

    return builder.as_markup()

def create_reply_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for button in buttons:
        builder.button(text=button)

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard
