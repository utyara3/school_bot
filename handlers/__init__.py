from aiogram import Dispatcher, Router
from handlers import common

ALL_ROUTERS: tuple[Router] = (
    common.router,
)


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров. Используется в main.py"""
    dp.include_routers(*ALL_ROUTERS)
