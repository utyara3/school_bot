from aiogram.fsm.state import StatesGroup, State


class Support(StatesGroup):
    waiting_message_to_support = State()


class Admin(StatesGroup):
    add_role_waiting_user_id = State()
    add_role_waiting_role = State()