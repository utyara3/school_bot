from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import handlers.states as states
from data.texts import messages as msg
import database.base as db

router = Router()


@router.message(Command('admin_panel'))
async def admin_panel_cmd(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id # type: ignore
    first_name = message.from_user.first_name # type: ignore
    is_user_admin: bool = await db.has_user_role(user_id, 'admin')

    if not is_user_admin:
        await message.answer(msg.ERRORS['acces_denied'])
        return

    await message.answer(
        msg.format_admin_panel_text(first_name),
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )