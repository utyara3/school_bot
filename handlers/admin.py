from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from data.texts import messages as msg
from filters.user_role import AccessFilter

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply

import database.core as db
import handlers.states as states


router = Router()
router.message.filter(AccessFilter('admin'))


@router.message(Command('admin_panel'))
async def admin_panel_cmd(message: Message, state: FSMContext) -> None:
    first_name = message.from_user.first_name # type: ignore

    await message.answer(
        msg.format_admin_panel_text(first_name),
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )


