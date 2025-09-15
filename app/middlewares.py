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
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message, Update

from app.config import TIMEZONE, ADMIN_CHAT_ID
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
            if not user.topic_id and (msg := event.message):
                from aiogram.enums import ParseMode
                from app.markups import admin as kb

                user_db = User(msg.from_user.id)
                if msg.from_user.username:
                    topic_name = f"{msg.from_user.username} {msg.from_user.id}"
                else:
                    topic_name = f"{msg.from_user.full_name} {msg.from_user.id}"
                result = await msg.bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
                topic_id = result.message_thread_id
                user_db.topic_id = topic_id
                user_info = (
                    f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                    f"ID: <code>{msg.from_user.id}</code>\n"
                    f"Username: @{msg.from_user.username}\n"
                    f"Тип пользователя: {user_db.type}"
                )
                user_db.tracking = True
                await msg.bot.send_message(
                    ADMIN_CHAT_ID,
                    message_thread_id=topic_id,
                    text=user_info,
                    reply_markup=kb.admin_menu(),
                    parse_mode=ParseMode.HTML,
                )
                user_db.tracking = False
                logging.info(f"Создан топик имени {msg.from_user.id} @{msg.from_user.username}")

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
            if not any(err in str(e) for err in ["message is not modified", "query is too old"]):
                logging.exception(e)
        except TelegramNetworkError:
            logging.error("TelegramNetworkError")
        except TelegramRetryAfter:
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


class TrackingMiddleware(BaseMiddleware):
    """Мидлварь, логирующая ивенты от пользователей в чат админа"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = User(data["event_from_user"].id)
        if (event.message and event.message.chat.id == ADMIN_CHAT_ID) or (
            event.callback_query and event.callback_query.message.chat.id == ADMIN_CHAT_ID
        ):
            return await handler(event, data)

        if user.tracking:
            if event.callback_query and not event.callback_query.from_user.is_bot:
                await event.bot.send_message(
                    ADMIN_CHAT_ID,
                    message_thread_id=user.topic_id,
                    text=event.callback_query.data,
                    parse_mode="HTML",
                )
            else:
                await event.bot.forward_message(
                    ADMIN_CHAT_ID,
                    message_thread_id=user.topic_id,
                    from_chat_id=user.id,
                    message_id=event.message.message_id,
                )
        return await handler(event, data)
