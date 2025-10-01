from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import handlers.states as states
import database.users as users_db
import database.support as support_db
from data.texts import messages as msg

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    user_id = message.from_user.id 
    username = message.from_user.username or '' 
    first_name = message.from_user.first_name 
    last_name = message.from_user.last_name or '' 
    if not await users_db.is_user_in_database(user_id):
        await users_db.insert_user_to_database(user_id, username, first_name, last_name)

    await message.answer(
        msg.COMMON["start"],
        reply_markup=kb_reply.start_kb().as_markup(resize_keyboard=True)
    )


@router.message(Command('cancel'))
async def cancel_cmd(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    keyboard = kb_reply.start_kb().as_markup(resize_keyboard=True)

    if not current_state:
        await message.answer(
            msg.ERRORS['nothing_to_cancel'],
            reply_markup=keyboard
        )
        return

    if current_state == "Support:waiting_supports_answer":
        current_data = await state.get_data()
        ticket = current_data['ticket_data']

        await support_db.set_ticket_status_pending(ticket['id'])
        await message.answer(msg.ERRORS['answer_cancelled'])
    
    await message.answer(
        msg.COMMON['cancel'],
        reply_markup=keyboard
    )
    await state.clear()


@router.message(F.text.lower().contains('поддержка'))
@router.message(Command('support'))
async def support(message: Message, state: FSMContext) -> None:
    await message.answer(msg.SUPPORT['support'])

    await state.set_state(states.Support.waiting_message_to_support)


@router.message(F.text, states.Support.waiting_message_to_support)
async def send_to_supports(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id 
    fullname = message.from_user.full_name or '' 

    support_ids: list[int] = await users_db.get_users_by_role('support')

    ticket_id = await support_db.create_ticket(user_id, message.text)

    keyboard = kb_inline.support_message_kb(ticket_id)

    for support_id in support_ids:
        await message.bot.send_message(
            chat_id=support_id, 
            text=msg.format_message_to_support(user_id, fullname, message.text, ticket_id),
            reply_markup=keyboard.as_markup()
        )

    await message.answer(msg.SUPPORT['sent_to_support'])
    await state.clear()
