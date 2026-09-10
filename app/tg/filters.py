from aiogram import MagicFilter, types
from aiogram.filters import BaseFilter

from app.core.config import config


class ChatTypeIdFilter(BaseFilter):
    """Фильтр, проверяющий тип чата и id, если указан, и возвращающий True или False"""

    def __init__(self, chat_type: list, chat_id: int | None = None) -> None:
        self.chat_id = chat_id
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool | None:
        if not bool(message.from_user.is_bot):
            if message.chat.type in self.chat_type and self.chat_id is not None:
                return str(message.chat.id) == str(config.admin_chat_id)
            return message.chat.type in self.chat_type
        return None


class IgnoreFilter(MagicFilter):
    def resolve(self, factory):
        return "ignore" in factory.action
