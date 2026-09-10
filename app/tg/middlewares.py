from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import Message, TelegramObject, Update
from sqlalchemy.ext.asyncio.session import AsyncSession
from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
)

from app.core.config import config
from app.core.enums import Platform
from app.database.session import session_scope
from app.services.user import UserService


log = structlog.get_logger()


class LoggingMiddleware:
    async def __call__(self, handler, event, data):
        clear_contextvars()

        user = data.get("event_from_user")
        bind_contextvars(
            platform="telegram",
            user_id=user.id,
        )

        try:
            return await handler(event, data)

        finally:
            clear_contextvars()


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        user = data.get("event_from_user")
        chat = data.get("event_chat")

        if user is None and user.is_bot and chat is None:
            return None

        async with session_scope() as session:
            data["session"]: AsyncSession = session
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
                log.exception()
        except TelegramNetworkError:
            log.exception()
        except TelegramRetryAfter:
            log.exception()


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
