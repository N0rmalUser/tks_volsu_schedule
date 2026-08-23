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

import asyncio

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app.common import set_logging
from app.common.schedule_parser import college_schedule_parser
from app.config import TZ, config
from app.tg import middlewares
from app.tg.handlers.admin import callback as admin_callback, message as admin_message
from app.tg.handlers.user import callback as user_callback, message as user_message, status as user_status


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    aiocron.crontab(config.college_cron, func=college_schedule_parser, tz=TZ)
    session = AiohttpSession()
    bot = Bot(token=config.tg_bot_token, session=session)
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


if __name__ == "__main__":
    set_logging("aiogram.event")
    asyncio.run(main())
