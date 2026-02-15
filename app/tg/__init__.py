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
import logging

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from app.common import BroadcastStates, create_progress_bar, set_logging
from app.common.schedule_parser import college_schedule_parser
from app.config import COLLEGE_CRON, TG_BOT_TOKEN
from app.config import TZ
from app.tg import handlers
from app.tg import markups
from app.tg import middlewares
from app.tg.handlers.admin import callback as admin_callback, message as admin_message
from app.tg.handlers.user import message as user_message, callback as user_callback, status as user_status


async def send_broadcast_message(msg: Message, state: FSMContext, message_id: int, user_ids: list[int]) -> None:
    from asyncio import sleep

    from app.database.user import User

    sent_count = 0
    total_users = len(user_ids)
    try:
        for user_id in user_ids:
            if await state.get_state() == BroadcastStates.cancel_sending.state:
                await msg.edit_text(text="Отправка отменена")
                break
            if not User(user_id).blocked:
                try:
                    await msg.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=msg.chat.id,
                        message_id=message_id,
                    )
                    sent_count += 1
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                finally:
                    await msg.edit_text(
                        text=f"Отправлено {sent_count} из {total_users} сообщений\n"
                             f"{create_progress_bar(sent_count, total_users)}",
                        reply_markup=markups.admin.cancel_sending(),
                    )
                    await sleep(1)
        logging.info("Отправлено сообщение всем пользователям")
        await msg.edit_text("Рассылка завершена!")
    except TypeError:
        await msg.edit_text("Ошибка при отправке сообщения")


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    aiocron.crontab(COLLEGE_CRON, func=college_schedule_parser, tz=TZ)
    session = AiohttpSession()
    bot = Bot(token=TG_BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(user_callback.router, user_message.router, user_status.router, admin_message.router,
                       admin_callback.router, )

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
