import asyncio
import logging

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.core.logging_config import setup_logging
from app.schemas.keyboard import init_keyboard_data
from app.tg import middlewares
from app.tg.handlers import (
    admin as admin_message,
    callback as user_callback,
    message as user_message,
    status as user_status,
)


log = structlog.get_logger()


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    setup_logging()
    await init_keyboard_data()

    aiogram_logger = logging.getLogger("aiogram.event")
    aiogram_logger.setLevel(logging.WARNING)

    session = AiohttpSession()
    bot = Bot(token=config.tg_bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        user_callback.router,
        user_message.router,
        user_status.router,
        admin_message.router,
    )
    dp.update.middleware(middlewares.LoggingMiddleware())
    dp.update.middleware(middlewares.SessionMiddleware())
    dp.update.middleware(middlewares.TrackingMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    log.info("bot_started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


if __name__ == "__main__":
    asyncio.run(main())
