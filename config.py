from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = getenv('BOT_TOKEN', '')
GENERAL_ADMINS: list[int] = [int(admin_id) for admin_id in getenv('GENERAL_ADMINS', "").split(",") if admin_id]
DATABASE_PATH: str = getenv('DATABASE_PATH', '')
LOGGER_NAME: str = getenv('LOGGER_NAME', 'school_bot')

assert BOT_TOKEN != ''
assert DATABASE_PATH != ''
