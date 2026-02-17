import logging
from datetime import datetime
from typing import Any

from vkbottle import ABCView, BaseMiddleware
from vkbottle.bot import Message

from app.config import TZ
from app.database.vkuser import VkUser


class RegistrationMiddleware(BaseMiddleware[Message]):
    def __init__(self, event: Any, view: ABCView | None) -> None:
        super().__init__(event, view)
        self.cached = False

    async def pre(self) -> None:
        user = VkUser(self.event.from_id)
        if not user.is_exists():
            user.start_date = datetime.now(TZ).isoformat()
            logging.info(f"Создан {user.id}")
