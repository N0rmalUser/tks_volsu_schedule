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

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app import middlewares
from app.config import BOT_TOKEN, COLLEGE_CRON, TZ
from app.handlers.admin import callback as admin_callback
from app.handlers.admin import message as admin_message
from app.handlers.user import callback as user_callback
from app.handlers.user import message as user_message
from app.handlers.user import status as user_status

from .misc.schedule_parser import college_schedule_parser


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    aiocron.crontab(COLLEGE_CRON, func=college_schedule_parser, tz=TZ)
    session = AiohttpSession()
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        user_callback.router,
        user_message.router,
        user_status.router,
        admin_message.router,
        admin_callback.router,
    )

    dp.update.middleware(middlewares.BanUsersMiddleware())
    dp.update.middleware(middlewares.TopicCreatorMiddleware())
    dp.update.middleware(middlewares.UserActivityMiddleware())
    dp.update.middleware(middlewares.TrackingMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


try:
    from .config import (
        DATA_PATH,
        DB_PATH,
        GROUPS_SCHEDULE_PATH,
        PLOT_PATH,
        ROOMS_SHEETS_PATH,
        SCHEDULE_PATH,
        TEACHERS_SHEETS_PATH,
    )

    for path in [
        DATA_PATH,
        DB_PATH,
        SCHEDULE_PATH,
        GROUPS_SCHEDULE_PATH,
        TEACHERS_SHEETS_PATH,
        ROOMS_SHEETS_PATH,
        PLOT_PATH,
    ]:
        path.mkdir(parents=True, exist_ok=True)
except ImportError as e:
    logging.error(e)
except Exception as e:
    logging.error(e)
