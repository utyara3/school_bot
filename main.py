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

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    #dp.include_router(commands.router)

    await bot.delete_webhook(
            drop_pending_updates=True
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
