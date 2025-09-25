from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
GENERAL_ADMINS = [int(admin_id) for admin_id in getenv('GENERAL_ADMINS', "").split(",") if admin_id]
DATABASE_PATH = getenv('DATABASE_PATH')
