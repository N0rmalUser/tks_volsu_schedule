from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import Message, Update, CallbackQuery

from data.config import THROTTLE_TIME

from datetime import datetime, timedelta

from typing import Union
from typing import Callable, Dict, Any, Awaitable
from aiogram.exceptions import TelegramBadRequest


class ChatTypeFilter(BaseFilter):
    """
    A filter that accepts the chat type and returns True or False
    :param chat_type:  The type of chat to be checked
    :type chat_type:  str or list
    """

    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class AntiSpamMessageMiddleware(BaseMiddleware):
    """
    A middleware that deletes messages that are sent too often
    """

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
        """
        Method that is called when a message is received
        :param handler:  Wrapped handler in middlewares chain
        :param event:  Incoming event (Subclass of :class:`aiogram.types.base.TelegramObject`)
        :param data:  Contextual data. Will be mapped to handler arguments
        :return:  :class:`Any`
        """

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


class IgnoreMessageNotModifiedMiddleware(BaseMiddleware):
    """
    Middleware that ignores the "message is not modified" error from Telegram.
    """
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        """
        Method that is called when an update is received.
        :param handler: Wrapped handler in middlewares chain.
        :param event: Incoming event (Subclass of :class:`aiogram.types.base.TelegramObject`).
        :param data: Contextual data. Will be mapped to handler arguments.
        :return: :class:`Any`
        """
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            if 'message is not modified' in str(e):
                await event.answer("Ты уже тут")
                return


class AntiSpamCallbackMiddleware(BaseMiddleware):
    """
    A middleware that deletes messages that are sent too often
    """

    def __init__(self):
        self.users_last_message_time = {}
        self.users_warned = set()
        self.spam_threshold = timedelta(seconds=1)

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        """
        Method that is called when a message is received
        :param handler:  Wrapped handler in middlewares chain
        :param event:  Incoming event (Subclass of :class:`aiogram.types.base.TelegramObject`)
        :param data:  Contextual data. Will be mapped to handler arguments
        :return:  :class:`Any`
        """

        if isinstance(event, CallbackQuery):
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
