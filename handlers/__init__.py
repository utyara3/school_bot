from aiogram import Dispatcher, Router
from handlers import common

ALL_ROUTERS: tuple[Router] = (
    common.router
)ф


def register_handlers(dp: Dispatcher) -> None:
    dp.include_routers(*ALL_ROUTERS)

