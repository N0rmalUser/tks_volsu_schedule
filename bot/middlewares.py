from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.types import Message, Update, CallbackQuery

from config import THROTTLE_TIME, timezone

from datetime import datetime, timedelta

from typing import Callable, Dict, Any, Awaitable

from bot.database.user import UserDatabase

import logging

import pytz


class AntiSpamMessageMiddleware(BaseMiddleware):
    """Мидлварь, удаляющая сообщения, отправленные слишком часто"""

    def __init__(self):
        self.users_last_message_time = {}
        self.users_warned = set()
        self.spam_threshold = timedelta(seconds=THROTTLE_TIME)

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message):
            user = event.from_user
            last_message_time = self.users_last_message_time.get(user.id)
            if last_message_time and datetime.now(datetime.now(pytz.timezone(timezone)).timetuple()) - last_message_time < self.spam_threshold:
                await event.delete()
                if user.id not in self.users_warned:
                    self.users_warned.add(user.id)
                return
            self.users_last_message_time[user.id] = datetime.now(datetime.now(pytz.timezone(timezone)).timetuple())
            self.users_warned.discard(user.id)
        return await handler(event, data)


class AntiSpamCallbackMiddleware(BaseMiddleware):
    """Мидлварь, игнорящая колбеки, отправленные слишком часто"""

    def __init__(self):
        self.users_last_message_time = {}
        self.users_warned = set()
        self.spam_threshold = timedelta(seconds=0.8)

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, CallbackQuery):
            user = event.from_user
            last_message_time = self.users_last_message_time.get(user.id)
            if last_message_time and datetime.now(datetime.now(pytz.timezone(timezone)).timetuple()) - last_message_time < self.spam_threshold:
                await event.answer("Не спамь")
                if user.id not in self.users_warned:
                    self.users_warned.add(user.id)
                return
            self.users_last_message_time[user.id] = datetime.now(datetime.now(pytz.timezone(timezone)).timetuple())
            self.users_warned.discard(user.id)
        return await handler(event, data)


class BanUsersMiddleware(BaseMiddleware):
    """Мидлварь, игнорящий все updates для забаненных пользователей"""

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user = UserDatabase(data['event_from_user'].id)

        if user.exists():
            if not user.banned:
                return await handler(event, data)
        else:
            return await handler(event, data)


class IgnoreMessageNotModifiedMiddleware(BaseMiddleware):
    """Мидлварь, игнорирующая ошибку "message is not modified" при попытке изменить сообщение"""

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            print("1")
            if 'message is not modified' in str(e):
                await event.answer("Выбран тот же день")
                return


class CallbackTelegramErrorsMiddleware(BaseMiddleware):
    """Мидлварь, обрабатывающая ошибки, возникающие при отправке колбеков в телеграмме"""
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        try:
            await handler(event, data)
        except TelegramBadRequest as e:
            logging.error("TelegramBadRequest")
        except TelegramNetworkError as e:
            logging.error("TelegramNetworkError")
        except TelegramRetryAfter as e:
            logging.error("TelegramRetryAfter 25 секунд")
