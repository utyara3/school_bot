from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.users import has_user_role
from data.texts import messages as msg


class AccessFilter(BaseFilter):
    def __init__(self, role: str) -> None:
        self.role = role

    async def __call__(self, message: Message) -> bool:
        bool_has_user_role = await has_user_role(message.from_user.id, self.role)
        if not bool_has_user_role:
            await message.answer(msg.ERRORS['access_denied'])
            
        return bool_has_user_role
    