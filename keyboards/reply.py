from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import data.texts.messages as msg


def start_kb():
    builder = ReplyKeyboardBuilder()

    for button_text in msg.REPLY_BUTTONS['start']:
        builder.add(KeyboardButton(text=button_text))

    builder.adjust(2)
    return builder


def admin_kb():
    builder = ReplyKeyboardBuilder()

    for button_text in msg.REPLY_BUTTONS['admin_panel']:
        builder.add(KeyboardButton(text=button_text))

    builder.adjust(2)
    return builder
