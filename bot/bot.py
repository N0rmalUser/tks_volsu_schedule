from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ChatMemberUpdated
from aiogram.utils.deep_linking import create_start_link

from bot import database as db, middlewares
from bot.handlers import admin, user
from bot.markups import admin_markups as kb
from config import BOT_TOKEN, ADMIN_CHAT_ID

import logging

bot: Bot
logger: logging.Logger
stream_handler: logging.StreamHandler


async def main() -> None:
    """Функция запуска бота,. Удаляет вебхуки и стартует поллинг."""
    global bot, logger, stream_handler
    logger = logging.getLogger(__name__)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S %d-%m-%Y')
    )
    logger.addHandler(stream_handler)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(user.callback_handler.router, user.message_handler.router, user.status_handler.router,
                       admin.message_handler.router)
    dp.message.middleware(middlewares.AntiSpamMessageMiddleware())
    dp.callback_query.middleware(middlewares.AntiSpamCallbackMiddleware())
    dp.callback_query.middleware(middlewares.IgnoreMessageNotModifiedMiddleware())
    dp.message.middleware(middlewares.TelegramBadRequestMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# Функции-обработчики команд из importlib (нельзя использовать в других файлах из-за зацикливания)

async def enable_logging(msg: Message):
    if stream_handler not in logger.handlers:
        logger.addHandler(stream_handler)
        await msg.reply("Логирование в терминал включено.")
    else:
        await msg.reply("Логирование в терминал уже включено.")


async def disable_logging(msg: Message):
    if stream_handler in logger.handlers:
        logger.removeHandler(stream_handler)
        await msg.reply("Логирование в терминал выключено.")
    else:
        await msg.reply("Логирование в терминал уже выключено.")


async def topic_create(msg: Message) -> None:
    """Создаёт личный топик юзера в админском чате. Если топик для этого пользователя определён в базе данных, ничего не делает."""
    global bot
    user_id = msg.from_user.id
    if db.get_topic_id(user_id):
        return
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {user_id}"
    else:
        topic_name = f"{msg.from_user.full_name} {str(user_id)}"

    result = await bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
    topic_id = result.message_thread_id
    db.set_topic_id(user_id, topic_id)
    user_info = (f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                 f"ID: <code>{user_id}</code>\n"
                 f"Username: @{msg.from_user.username}\n"
                 f"Номер телефона: {msg.contact}\n"
                 f"Пригласил: <code>{db.get_inviter(user_id) if db.get_inviter(user_id) else 'Никто'}</code>\n"
                 f"Тип пользователя: {db.get_user_type(user_id)}")
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=topic_id, text=user_info, reply_markup=kb.admin_menu,
                           parse_mode="HTML")
    db.set_tracking(msg.from_user.id, False)


async def start_message(msg: Message, user_id: int, menu, keyboard) -> None:
    """Отправляет сообщение при старте бота. Создаёт топик пользователя. Отправляет ссылку для приглашения и меню."""
    global bot
    link = await create_start_link(bot, f"{user_id}={db.get_user_type(user_id)}", encode=True)
    await msg.answer(f"Привет, {msg.from_user.full_name}\n"
                     f"Вот ссылка для приглашения: {link}",
                     reply_markup=menu)
    await msg.answer("Выбери себя в списке", reply_markup=keyboard)
    await topic_create(msg)


async def admin_sender(msg: Message) -> None:
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=db.get_topic_id(msg.from_user.id),
                           text="Юзверь просит помощи админа @n0rmal_user")


async def send_to_user(msg: Message) -> None:
    await bot.send_message(db.get_user_id(msg.message_thread_id), text=msg.text)


async def broadcast(msg: Message) -> None:
    await db.broadcast_message(bot, msg.text)


async def send_callback(callback: Message) -> None:
    if db.get_tracking(callback.from_user.id):
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=db.get_topic_id(callback.from_user.id),
                               text=callback.data)


async def send_user_status(event: ChatMemberUpdated, status: str) -> None:
    await bot.send_message(ADMIN_CHAT_ID, f"Пользователь @{event.from_user.username} {status} бота",
                           message_thread_id=db.get_topic_id(event.from_user.id))
