from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from data.texts import message as msg
from keyboards

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()  
    await message.answer(msg.COMMON["start"])
