from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ChatMemberUpdated, Document
from aiogram.utils.deep_linking import create_start_link

from bot import middlewares
from bot.database.utils import all_user_ids
from bot.database.user import UserDatabase
from bot.handlers import admin, user
from bot.markups import admin_markups as kb

from config import BOT_TOKEN, ADMIN_CHAT_ID

import logging


bot: Bot


async def main() -> None:
    """Функция запуска бота. Удаляет веб хуки и стартует поллинг."""
    global bot
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(user.callback_handler.router, user.message_handler.router, user.status_handler.router, admin.message_handler.router)

    dp.update.middleware(middlewares.BanUsersMiddleware())
    dp.callback_query.middleware(middlewares.IgnoreMessageNotModifiedMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


# Функции-обработчики команд из importlib (нельзя использовать в других файлах из-за зацикливания)


async def topic_create(msg: Message) -> None:
    """Создаёт личный топик юзера в админском чате. Если топик для этого пользователя определён в базе данных, ничего не делает."""
    global bot
    user = UserDatabase(msg.from_user.id)
    if user.topic_id:
        return
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {msg.from_user.id}"
    else:
        topic_name = f"{msg.from_user.full_name} {str(msg.from_user.id)}"
    result = await bot.create_forum_topic(ADMIN_CHAT_ID, topic_name, icon_custom_emoji_id="5312016608254762256")\
        if user.type == "teacher"\
        else await bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
    topic_id = result.message_thread_id
    user.topic_id = topic_id
    inviter = user.inviter_id
    user_info = (f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                 f"ID: <code>{msg.from_user.id}</code>\n"
                 f"Username: @{msg.from_user.username}\n"
                 f"Пригласил: <code>{inviter if inviter else 'Никто'}</code>\n"
                 f"Тип пользователя: {user.type}")
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=topic_id, text=user_info, reply_markup=kb.admin_menu, parse_mode="HTML")
    user.tracking = False
    logging.info(f'Создан топик имени {msg.from_user.id} @{msg.from_user.username}')


async def start_message(msg: Message, menu, keyboard) -> None:
    """Отправляет сообщение при старте бота. Создаёт топик пользователя. Отправляет ссылку для приглашения и меню."""
    global bot
    user = UserDatabase(msg.from_user.id)
    link = await create_start_link(bot, f"{msg.from_user.id}={user.type}", encode=True)
    await msg.answer(f"Привет, {msg.from_user.full_name}\n"
                     f"Вот ссылка для приглашения: {link}",
                     reply_markup=menu)
    await msg.answer("Выбери себя в списке", reply_markup=keyboard)
    await topic_create(msg)


async def admin_sender(msg: Message) -> None:
    """Отправляет крик о помощи в админский чат"""
    user = UserDatabase(msg.from_user.id)
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id,
                           text="Юзверь просит помощи админа @n0rmal_user")
    logging.warning(f'Юзверь {msg.from_user.id} @{msg.from_user.username} просит помощи админа')


async def send_to_user(msg: Message) -> None:
    from bot.database.user import UserDatabase
    await bot.send_message(UserDatabase(topic_id=msg.message_thread_id).tg_id(), text=msg.text)


async def get_file(msg: Document, existing_file):
    """Получает файл с расписанием и заменяет им текущее расписание"""
    file_id = msg.document.file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(existing_file, 'wb') as new_file:
        new_file.write(downloaded_file.read())


async def send_custom_message(user_id: int, text: str):
    """Отправляет пользователю кастомное сообщение."""
    await bot.send_message(user_id, text)


async def broadcast(msg: Message) -> None:
    """Отправляет сообщение всем пользователям, не заблокировавшим бота."""
    from asyncio import sleep
    user_ids = all_user_ids()
    for user_id in user_ids:
        if not UserDatabase(user_id).blocked:
            try:
                await bot.send_message(user_id, msg.text)
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            finally:
                await sleep(0.5)
    logging.info('Отправлено сообщение всем пользователям')


async def send_callback(callback: Message) -> None:
    """Отправляет сообщение в личный топик пользователя при нажатии на инлайн кнопку."""
    user = UserDatabase(callback.from_user.id)
    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id,
                               text=callback.data)


async def send_user_status(event: ChatMemberUpdated, status: str) -> None:
    """Отправляет сообщение в админский чат о статусе пользователя (заблокировал или разблокировал бота)."""
    user = UserDatabase(event.from_user.id)
    await bot.send_message(ADMIN_CHAT_ID, f"Пользователь @{event.from_user.username} {status} бота",
                           message_thread_id=user.topic_id)
