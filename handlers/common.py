from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import handlers.states as states
from data.texts import messages as msg

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    await message.answer(
        msg.COMMON["start"],
        reply_markup=kb_reply.start_kb().as_markup(resize_keyboard=True)
    )

@router.message(F.text.lower().contains('поддержка'))
@router.message(Command('support'))
async def support(message: Message, state: FSMContext) -> None:
    await message.answer(msg.COMMON['support'])

    await state.set_state(states.Support.waiting_message)
