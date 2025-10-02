from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from data.texts import messages as msg


def support_message_kb(ticket_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=msg.INLINE_BUTTONS['support_answer_button_text'],
            callback_data=f"support_answer:{ticket_id}"
        ),
    )

    return builder
    

def users_pagination_kb(current_page, total_page):
    ...
    