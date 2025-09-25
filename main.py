import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import register_handlers
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()

    register_handlers(dp)

    await bot.delete_webhook(
        drop_pending_updates=True
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
