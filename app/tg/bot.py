import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.core.logger import set_logging
from app.tg import middlewares
from app.tg.handlers import (
    admin as admin_message,
    callback as user_callback,
    message as user_message,
    status as user_status,
)


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует polling."""

    set_logging("aiogram.event")

    session = AiohttpSession()
    bot = Bot(token=config.tg_bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        user_callback.router,
        user_message.router,
        user_status.router,
        admin_message.router,
    )
    dp.update.middleware(middlewares.SessionMiddleware())
    dp.update.middleware(middlewares.TrackingMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


if __name__ == "__main__":
    asyncio.run(main())
