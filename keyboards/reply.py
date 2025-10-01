from typing import Coroutine
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import data.texts.messages as msg

from database.users import get_all_roles, get_user_roles


def _base(elements: list, adj: int) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    for element in elements:
        builder.add(KeyboardButton(text=element))
    
    builder.adjust(adj)
    return builder


def start_kb() -> ReplyKeyboardBuilder:
    return _base(msg.REPLY_BUTTONS['start'], 2)


def admin_kb() -> ReplyKeyboardBuilder:
    return _base(msg.REPLY_BUTTONS['admin_panel'], 2)


async def all_roles_kb() -> ReplyKeyboardBuilder:
    roles: list[str] = await get_all_roles()
    return _base(roles, 2)


def user_roles_kb(user_roles: list[str]) -> ReplyKeyboardBuilder:
    if 'student' in user_roles:
        user_roles.remove('student')

    return _base(user_roles, 2)

