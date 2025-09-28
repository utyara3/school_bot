import sys
import os

# Абсолютные импорты
sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import aiogram.exceptions as aioexcepts

from handlers import register_handlers
from database import base as db
from config import BOT_TOKEN, GENERAL_ADMINS, LOGGER_NAME
from utils.bot_logging import setup_logging, get_logger

setup_logging(
    name=LOGGER_NAME,
    log_file='bot.log',
    level=logging.INFO
)


async def main() -> None:
    main_logger = get_logger('main')
    main_logger.info("Запуск бота...")

    # Инициализируем базу данных
    await db.init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()

    for admin_id in GENERAL_ADMINS:
        if not await db.is_user_in_database(admin_id):
            try:
                chat = await bot.get_chat(admin_id)
            except aioexcepts.TelegramBadRequest: # Чат с админом не создан
                continue

            user_id = chat.id
            username = chat.username or ''
            first_name = chat.first_name or ''
            last_name = chat.last_name or ''

            await db.insert_user_to_database(user_id, username, first_name, last_name, ('admin', ))

    main_logger.info("Основные админы были добавлены в базу данных")

    # Регистрируем хендлеры
    register_handlers(dp)
    main_logger.info("Хендлеры были зарегестрированы")

    await bot.delete_webhook(
        drop_pending_updates=True
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
