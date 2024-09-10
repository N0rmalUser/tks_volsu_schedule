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
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.types import CallbackQuery, Message, Update

from bot.database.user import UserDatabase


class BanUsersMiddleware(BaseMiddleware):
    """Мидлварь, игнорящий все updates для забаненных пользователей"""

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        user = UserDatabase(data["event_from_user"].id)

        if user.exists():
            if not user.banned:
                return await handler(event, data)
        else:
            return await handler(event, data)


class IgnoreMessageNotModifiedMiddleware(BaseMiddleware):
    """Мидлварь, игнорирующая ошибку "message is not modified" при попытке изменить сообщение"""

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            print("1")
            if "message is not modified" in str(e):
                await event.answer("Выбран тот же день")
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
            # logging.exception(e)
        except TelegramNetworkError as e:
            logging.error("TelegramNetworkError")
        except TelegramRetryAfter as e:
            logging.error("TelegramRetryAfter 25 секунд")
