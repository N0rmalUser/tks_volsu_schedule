from aiogram.filters import BaseFilter
from aiogram.types import Message

from typing import Union


class ChatTypeFilter(BaseFilter):
    """
    Фильтр, проверяющий тип чата и возвращающий True или False
    :param chat_type:  Тип чата, который хотите проверить (private, group, supergroup, channel)
    :call_type chat_type:  str или list
    """
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
