import database.users as users_db
import keyboards.inline as inline_kb
import data.texts.messages as msg


class UserPagination:
    def __init__(self, users_per_page: int) -> None:
        self.users_per_page = users_per_page

    async def get_users_page(self, role: str, page: int = 1) -> dict:
        offset = (page - 1) * self.users_per_page

        total_pages = await users_db.get_number_of_users()
        users = await users_db.get_users(self.users_per_page, offset)
        keyboard = inline_kb.users_pagination_kb(page, total_pages)

        text = self.format_page(users, role)

        return text, keyboard

    def format_page(self, users: list[dict], role: str):
        ret_users = f"👥 <b>Пользователи с ролью <code>{role}</code>:</b>\n\n"
        for user in users:
            ret_users += msg.format_user_info(user)
            ret_users += "\n\n"

        return ret_users
    