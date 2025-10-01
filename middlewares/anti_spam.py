from time import time
from collections import defaultdict
from typing import Any, Callable
from random import choice

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


from config import (
    ANTI_SPAM_MESSAGES_PER_SECOND_WARN,
    ANTI_SPAM_MESSAGES_PER_SECOND_IGNORE
)
import data.texts.messages as msg


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(
        self, 
        messages_per_second_warn: int = ANTI_SPAM_MESSAGES_PER_SECOND_WARN,
        messages_per_second_ignore: int = ANTI_SPAM_MESSAGES_PER_SECOND_IGNORE
    ) -> None:
        # последняя очистка пользователей
        self._last_cleanup = time()
        # количество сообщений в секунду для того
        # чтобы написать предупреждение
        self.messages_per_second_warn = messages_per_second_warn
        # количество сообщений в секунду 
        # для игнорирования запросов
        self.messages_per_second_ignore = messages_per_second_ignore
        #defaultdict для того чтобы обращаться к
        #нусуществующим элементам словаря без ошибок
        self.user_data: dict = defaultdict(list)

    async def __call__(
        self, 
        handler: Callable, 
        event: TelegramObject, 
        data: dict[str, Any]
    ) -> Any:
        #очистка старых пользователей
        self._cleanup_old_users()        

        user_id = event.from_user.id 
        now = time()

        # перезаписываем список, где перебираем все значения, и оставляем
        # только те, которые были добавлены больше секунды назад
        self.user_data[user_id] = [t for t in self.user_data[user_id] if now - t <= 1]
        
        # добавляем текущее время отправки сообщения
        self.user_data[user_id].append(now)

        messages_count = len(self.user_data[user_id])
    
        # если больше игнор порога - игнорируем
        if messages_count > self.messages_per_second_ignore:
            return

        # если больше порога для предупреждения - предупреждаем
        elif messages_count > self.messages_per_second_warn:
            if hasattr(event, 'answer'):
                await event.answer(choice(msg.ERRORS['anti_spam'])) 
            return
        
        # иначе пропускаем запрос
        return await handler(event, data)

    def _cleanup_old_users(self) -> None:
        now = time()
        # если с момента последней очистки прошло больше 300 секунд
        if now - self._last_cleanup < 300: # 5 минут
            return
        
        cutoff_time = now - 600 # 10 минут

        # список неактивных пользователей (тех, у кого последнее время > 10 мин.)
        inactive_users = [
            user_id for user_id, timestamps in list(self.user_data.items())
            if not timestamps or timestamps[-1] < cutoff_time
        ]

        # удаляем неактивных пользователей
        for user_id in inactive_users:
            del self.user_data[user_id]

        # перезаписываем время последней очистки
        self._last_cleanup = now
        