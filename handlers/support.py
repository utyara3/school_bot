from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import handlers.states as states
import database.users as users_db
import database.support as support_db
from data.texts import messages as msg
from filters.user_role import AccessFilter

router = Router()


@router.callback_query(F.data.startswith('support_answer'), AccessFilter('support'))
async def support_answer(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    target_ticket_id = int(callback.data.split(":")[1])
    ticket = await support_db.get_ticket(target_ticket_id)

    if not ticket:
        await callback.message.answer(msg.ERRORS["ticket_not_found"])
        return

    status = ticket['status']

    if status != 'pending':
        if status == 'in_progress':
            await callback.message.answer(msg.ERRORS["ticket_already_in_progress"])
            await callback.answer()
            return
        
        await callback.message.answer(msg.ERRORS["ticket_already_resolved"])
        await callback.answer()
        return

    support_id = callback.from_user.id
    
    await support_db.set_ticket_status_in_progress(target_ticket_id, support_id)
    await callback.message.answer(msg.SUPPORT['support_decide_to_answer'])

    await callback.answer()
    await state.update_data(
        ticket_data={
            'id': ticket['id'],
            'user_id': ticket['user_id']
        }
    )
    await state.set_state(states.Support.waiting_supports_answer)


@router.message(states.Support.waiting_supports_answer, AccessFilter('support'))
async def send_supports_answer_to_user(message: Message, state: FSMContext) -> None:
    current_data = await state.get_data()
    
    ticket_id, user_id = current_data['ticket_data'].values()
    answer = message.text

    await message.bot.send_message(
        chat_id=user_id,
        text=msg.format_message_from_support(answer)
    )

    await message.answer(
        msg.SUCCESSES['support_answer_sent'],
        reply_markup=kb_reply.start_kb().as_markup(resize_keyboard=True)
    )
    
    await support_db.set_ticket_status_resolved(ticket_id, answer)
    await state.clear()
