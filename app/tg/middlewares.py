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
from collections.abc import Awaitable, Callable, Coroutine
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message, TelegramObject, Update

from app.core.config import config
from app.database.session import session_scope
from app.schemas.enums import Platform
from app.services.user import UserService


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.session import AsyncSession


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        user = data.get("event_from_user")
        chat = data.get("event_chat")

        if user is None:
            return await handler(event, data)
        if user.is_bot:
            return await handler(event, data)

        if chat is not None:
            async with session_scope() as session:
                data["session"]: AsyncSession = session
                return await handler(event, data)

        return await handler(event, data)


class CallbackTelegramErrorsMiddleware(BaseMiddleware):
    """Мидлварь, обрабатывающая ошибки, возникающие при отправке колбеков в телеграмме"""

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> None:
        try:
            await handler(event, data)
        except TelegramBadRequest as e:
            if not any(err in str(e) for err in ["message is not modified", "query is too old"]):
                logging.exception(e)
        except TelegramNetworkError:
            logging.error("TelegramNetworkError")
        except TelegramRetryAfter:
            logging.error("TelegramRetryAfter 25 секунд")


class TrackingMiddleware(BaseMiddleware):
    """Мидлварь, логирующая ивенты от пользователей в чат админа"""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Coroutine[Any, Any, Any]:

        user_id = int(data["event_from_user"].id)
        session: AsyncSession = data.get("session")
        service = await UserService.create(session, Platform.TELEGRAM, user_id)

        if (event.message and event.message.chat.id == config.admin_chat_id) or (
            event.callback_query and event.callback_query.message.chat.id == config.admin_chat_id
        ):
            return await handler(event, data)

        tracked = await service.get_tg_tracking()
        if tracked:
            topic_id = await service.get_tg_topic_id()
            if event.callback_query and not event.callback_query.from_user.is_bot:
                await event.bot.send_message(
                    config.admin_chat_id,
                    message_thread_id=topic_id,
                    text=event.callback_query.data,
                    parse_mode="HTML",
                )
            else:
                await event.bot.forward_message(
                    config.admin_chat_id,
                    message_thread_id=topic_id,
                    from_chat_id=user_id,
                    message_id=event.message.message_id,
                )
        return await handler(event, data)
