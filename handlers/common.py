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


@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    user_id = message.from_user.id # type: ignore
    username = message.from_user.username or '' # type: ignore
    first_name = message.from_user.first_name # type: ignore
    last_name = message.from_user.last_name or '' # type: ignore
    if not await db.is_user_in_database(user_id):
        await db.insert_user_to_database(user_id, username, first_name, last_name)

    await message.answer(
        msg.COMMON["start"],
        reply_markup=kb_reply.start_kb().as_markup(resize_keyboard=True)
    )


@router.message(Command('cancel'))
async def cancel_cmd(message: Message, state: FSMContext) -> None:
    await message.answer(
        msg.COMMON['cancel'],
        reply_markup=kb_reply.start_kb().as_markup(resize_keyboard=True)
    )
    await state.clear()


@router.message(F.text.lower().contains('поддержка'))
@router.message(Command('support'))
async def support(message: Message, state: FSMContext) -> None:
    await message.answer(msg.SUPPORT['support'])

    await state.set_state(states.Support.waiting_message)


@router.message(F.text, states.Support.waiting_message)
async def send_to_supports(bot: Bot, message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id # type: ignore
    fullname = message.from_user.fullname or '' # type: ignore

    support_ids: list[int] = await db.get_users_by_role('support')

    for support_id in support_ids:
        await bot.send_message(chat_id=support_id, 
                               text=msg.format_message_to_suppport(user_id, fullname, message.text))

    await message.answer(msg.SUPPORT['sent_to_support'])
    await state.clear()


@router.message()
async def test(message: Message):
    await message.answer("Не знаю такого...")
