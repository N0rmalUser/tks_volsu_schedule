# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

import pytz
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.types import Message, Update

from app.config import TIMEZONE
from app.database.activity import log_user_activity
from app.database.user import User


class BanUsersMiddleware(BaseMiddleware):
    """Мидлварь, игнорящий все updates для забаненных пользователей"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = User(data["event_from_user"].id)
        if user.is_exists:
            if not user.banned:
                return await handler(event, data)
        else:
            return await handler(event, data)


class TopicCreatorMiddleware(BaseMiddleware):
    """Мидлварь, создающий топик пользователя, если он не создан"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = User(data["event_from_user"].id)
        if (event.message and not event.message.from_user.is_bot) or (
            event.callback_query and not event.callback_query.from_user.is_bot
        ):
            if not user.topic_id:
                from app import topic_create

                if msg := event.message:
                    await topic_create(msg)
            return await handler(event, data)
        return


class CallbackTelegramErrorsMiddleware(BaseMiddleware):
    """Мидлварь, обрабатывающая ошибки, возникающие при отправке колбеков в телеграмме"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        try:
            await handler(event, data)
        except TelegramBadRequest as e:
            logging.error("TelegramBadRequest")
            if not any(err in str(e) for err in ["message is not modified", "query is too old"]):
                logging.exception(e)
        except TelegramNetworkError as e:
            logging.error("TelegramNetworkError")
        except TelegramRetryAfter as e:
            logging.error("TelegramRetryAfter 25 секунд")


class UserActivityMiddleware(BaseMiddleware):
    """Мидлварь, логирующая ивенты от пользователей в бд"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user_id = data["event_from_user"].id
        User(user_id).last_date = datetime.now(pytz.timezone(TIMEZONE)).isoformat()
        log_user_activity(user_id)
        return await handler(event, data)
