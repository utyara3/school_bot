from aiogram import Dispatcher, Router
from handlers import common, admin

ALL_ROUTERS: tuple[Router, Router] = (
    common.router,
    admin.router,
)


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров. Используется в main.py"""
    dp.include_routers(*ALL_ROUTERS)
