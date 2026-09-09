from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
)
from vkbottle import BaseMiddleware


class LoggingMessageMiddleware(BaseMiddleware):
    async def pre(self):
        clear_contextvars()

        bind_contextvars(
            platform="vk",
            user_id=self.event.from_id,
        )


class LoggingRawEventMiddleware(BaseMiddleware):
    async def pre(self):
        clear_contextvars()

        bind_contextvars(
            platform="vk",
            user_id=self.event.get("object").get("user_id"),
        )
