from aiogram.fsm.state import StatesGroup, State


class Support(StatesGroup):
    waiting_message_to_support = State()
    waiting_supports_answer = State()
    ticket_data = State()


class Admin(StatesGroup):
    admin_panel = State()
    
    add_role_waiting_user_id = State()
    add_role_waiting_role = State()

    remove_role_waiting_user_id = State()
    remove_role_waiting_role = State()
