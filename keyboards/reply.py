from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import data.texts.messages as msg

from database.users import get_all_roles


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


async def user_roles_kb():
    builder = ReplyKeyboardBuilder()
    roles = await get_all_roles()

    for role in roles:
        builder.add(KeyboardButton(text=role))

    builder.adjust(2)
    return builder
