from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from data.texts import messages as msg
from filters.user_role import AccessFilter

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply

import database.core as core_db
import database.users as users_db
import handlers.states as states


router = Router()
router.message.filter(AccessFilter('admin'))


@router.message(Command('admin_panel'))
async def admin_panel_cmd(message: Message, state: FSMContext) -> None:
    first_name = message.from_user.first_name 

    await message.answer(
        msg.format_admin_panel_text(first_name),
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )

    await state.clear()


@router.message(F.text.lower().contains("добавить роль"))
async def admin_add_role_waiting_user_id(message: Message, state: FSMContext) -> None:
    await message.answer(msg.ADMIN['add_role_enter_id'])

    await state.set_state(states.Admin.add_role_waiting_user_id)


@router.message(F.text, states.Admin.add_role_waiting_user_id)
async def admin_add_role_waiting_role(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit(): 
        await message.answer(msg.ERRORS['user_id_NaN'])
        return

    user_id = int(message.text)

    if not await users_db.is_user_in_database(user_id):
        await message.answer(msg.ERRORS['user_not_in_database'])
        return
    
    keyboard = await kb_reply.user_roles_kb()

    await message.answer(
        msg.ADMIN['add_role_choose_role'],
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(add_role_waiting_user_id=user_id)
    await state.set_state(states.Admin.add_role_waiting_role)


@router.message(F.text, states.Admin.add_role_waiting_role)
async def admin_add_role(message: Message, state: FSMContext) -> None:
    role = message.text
    all_roles = await users_db.get_all_roles()

    if role not in all_roles:
        await message.answer(msg.ERRORS['role_not_found'])
        return
    
    data = await state.get_data()
    user_id = data['add_role_waiting_user_id']

    if await users_db.has_user_role(user_id, role):
        await message.answer(msg.ERRORS['user_already_have_role'])
        return
    
    await users_db.add_role_to_user(user_id, role)

    await message.answer(
        msg.SUCCESSES['role_added'],
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )

    await state.clear()
    