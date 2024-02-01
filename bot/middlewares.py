from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, Update, CallbackQuery

from config import THROTTLE_TIME

from datetime import datetime, timedelta

from typing import Callable, Dict, Any, Awaitable

from bot import database as db

import importlib

import logging


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
            if last_message_time and datetime.now() - last_message_time < self.spam_threshold:
                await event.delete()
                if user.id not in self.users_warned:
                    self.users_warned.add(user.id)
                return
            self.users_last_message_time[user.id] = datetime.now()
            self.users_warned.discard(user.id)
        return await handler(event, data)


class AntiSpamCallbackMiddleware(BaseMiddleware):
    """Мидлварь, игнорящая колбеки, отправленные слишком часто"""

    def __init__(self):
        self.users_last_message_time = {}
        self.users_warned = set()
        self.spam_threshold = timedelta(seconds=0.5)

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, CallbackQuery):
            user = event.from_user
            last_message_time = self.users_last_message_time.get(user.id)
            if last_message_time and datetime.now() - last_message_time < self.spam_threshold:
                await event.answer("Не спамь")
                if user.id not in self.users_warned:
                    self.users_warned.add(user.id)
                return
            self.users_last_message_time[user.id] = datetime.now()
            self.users_warned.discard(user.id)
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
            if 'message is not modified' in str(e):
                await event.answer("Ты уже тут")
                return


class TelegramBadRequestMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        try:
            await handler(event, data)
        except TelegramBadRequest as e:
            if "message thread not found" in str(e):
                logging.warning(f"Не удалось найти топик юзера {event.from_user.id}")
                db.delete_topic_id(event.from_user.id)
                await getattr(importlib.import_module("bot.bot"), "topic_create")(event)
                await handler(event, data)
            else:
                return
