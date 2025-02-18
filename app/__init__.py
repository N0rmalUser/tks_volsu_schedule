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

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from app import middlewares
from app.config import ADMIN_CHAT_ID, BOT_TOKEN
from app.database.user import User
from app.handlers import admin, user
from app.markups import admin as kb
from . import database, filters, handlers, markups, middlewares, misc


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    session = AiohttpSession()
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(user.callback.router, user.message.router, user.status.router, admin.message.router,
                       admin.callback.router, )

    dp.update.middleware(middlewares.BanUsersMiddleware())
    dp.update.middleware(middlewares.TopicCreatorMiddleware())
    dp.update.middleware(middlewares.UserActivityMiddleware())
    dp.update.middleware(middlewares.TrackingMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


async def start_message(msg: Message, menu, keyboard) -> None:
    """Отправляет сообщение при старте бота. Создаёт топик пользователя. Отправляет ссылку для приглашения и меню."""

    await msg.answer(f"Привет, {msg.from_user.full_name}\n", reply_markup=menu, )
    await msg.answer("Выбери себя в списке", reply_markup=keyboard)

    if not msg.from_user.is_bot and not User(msg.from_user.id).topic_id:
        await topic_create(msg)


async def topic_create(msg: Message) -> None:
    user_db = User(msg.from_user.id)
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {msg.from_user.id}"
    else:
        topic_name = f"{msg.from_user.full_name} {msg.from_user.id}"
    result = await msg.bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
    topic_id = result.message_thread_id
    user_db.topic_id = topic_id
    user_info = (f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                 f"ID: <code>{msg.from_user.id}</code>\n"
                 f"Username: @{msg.from_user.username}\n"
                 f"Тип пользователя: {user_db.type}")
    user_db.tracking = True
    await msg.bot.send_message(ADMIN_CHAT_ID, message_thread_id=topic_id, text=user_info,
                               reply_markup=kb.admin_menu(), )
    user_db.tracking = False
    logging.info(f"Создан топик имени {msg.from_user.id} @{msg.from_user.username}")
