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

from utils.bot_logging import get_logger
from utils.pagination import UserPagination

router = Router()
logger = get_logger('handlers.admin')


@router.message(Command('admin_panel'), AccessFilter('admin'))
async def admin_panel_cmd(message: Message, state: FSMContext) -> None:
    first_name = message.from_user.first_name 

    await message.answer(
        msg.format_admin_panel_text(first_name),
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )

    await state.set_state(states.Admin.admin_panel)


@router.message(
        F.text.lower().contains("добавить роль"), 
        states.Admin.admin_panel, 
        AccessFilter('admin')
)
async def admin_add_role_waiting_user_id(message: Message, state: FSMContext) -> None:
    await message.answer(msg.ADMIN['add_role_enter_id'])

    await state.set_state(states.Admin.add_role_waiting_user_id)


@router.message(F.text, states.Admin.add_role_waiting_user_id, AccessFilter('admin'))
async def admin_add_role_waiting_role(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit(): 
        await message.answer(msg.ERRORS['user_id_NaN'])
        return

    user_id = int(message.text)

    if not await users_db.is_user_in_database(user_id):
        await message.answer(msg.ERRORS['user_not_in_database'])
        return

    all_roles: list[str] = await users_db.get_all_roles()
    user_roles: list[str] = await users_db.get_user_roles(user_id)

    roles = list(set(all_roles)^set(user_roles))

    if not roles:
        await message.answer(
            msg.ERRORS['no_role_to_add'],
            reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
        )
        await state.set_state(states.Admin.admin_panel)
        return
    
    keyboard = kb_reply.user_roles_kb(roles)

    await message.answer(
        msg.ADMIN['add_role_choose_role'],
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(add_role_waiting_user_id=user_id)
    await state.set_state(states.Admin.add_role_waiting_role)


@router.message(F.text, states.Admin.add_role_waiting_role, AccessFilter('admin'))
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
    
    logger.info(f"Пользователь ({message.from_user.id}) запрашивает "\
                f"добавление роли ({role}) пользователю ({user_id})")
    
    await users_db.add_role_to_user(user_id, role)


    await message.answer(
        msg.SUCCESSES['role_added'],
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )

    await state.set_state(states.Admin.admin_panel)


@router.message(
    F.text.lower().contains('убрать роль'), 
    states.Admin.admin_panel,
    AccessFilter('admin')
)
async def remove_role_waiting_user_id(message: Message, state: FSMContext) -> None:
    await message.answer(msg.ADMIN['remove_role_enter_id'])
    
    await state.set_state(states.Admin.remove_role_waiting_user_id)


@router.message(F.text, states.Admin.remove_role_waiting_user_id, AccessFilter('admin'))
async def remove_role_waiting_role(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit(): 
        await message.answer(msg.ERRORS['user_id_NaN'])
        return

    user_id = int(message.text)

    if not await users_db.is_user_in_database(user_id):
        await message.answer(msg.ERRORS['user_not_in_database'])
        return
    
    all_roles = await users_db.get_user_roles(user_id)
    user_roles = [role for role in all_roles if role != 'student']

    if not user_roles:
        await message.answer(
            msg.ERRORS['no_roles_to_delete'],
            reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
        )
        await state.set_state(states.Admin.admin_panel)
        return
    
    keyboard = kb_reply.user_roles_kb(user_roles)

    await message.answer(
        msg.ADMIN['remove_role_choose_role'],
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(remove_role_waiting_user_id=user_id)
    await state.set_state(states.Admin.remove_role_waiting_role)


@router.message(F.text, states.Admin.remove_role_waiting_role, AccessFilter('admin'))
async def admin_remove_role(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data['remove_role_waiting_user_id']

    all_roles = await users_db.get_user_roles(user_id)
    user_roles = [role for role in all_roles if role != 'student']

    role = message.text
    if role not in user_roles:
        await message.answer(msg.ERRORS['role_not_found'])
        return
    
    logger.info(f"Пользователь ({message.from_user.id}) запрашивает "\
                f"удаление роли ({role}) пользователю ({user_id})")

    await users_db.remove_role_for_user(user_id, role)

    await message.answer(
        msg.SUCCESSES['role_removed'],
        reply_markup=kb_reply.admin_kb().as_markup(resize_keyboard=True)
    )

    await state.set_state(states.Admin.admin_panel)


@router.message(F.text.lower().contains('пользователи'), states.Admin.admin_panel, AccessFilter('admin'))
async def admin_users(message: Message, state: FSMContext) -> None:
    ...
