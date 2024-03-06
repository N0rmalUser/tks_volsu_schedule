from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ChatMemberUpdated, Document
from aiogram.utils.deep_linking import create_start_link

from bot import database as db, middlewares
from bot.handlers import admin, user
from bot.markups import admin_markups as kb
from config import BOT_TOKEN, ADMIN_CHAT_ID

import logging

import os

bot: Bot


async def main() -> None:
    """Функция запуска бота,. Удаляет вебхуки и стартует поллинг."""
    global bot
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(user.callback_handler.router, user.message_handler.router, user.status_handler.router, admin.message_handler.router)

    dp.update.middleware(middlewares.BanUsersMiddleware())
    dp.message.middleware(middlewares.AntiSpamMessageMiddleware())
    dp.callback_query.middleware(middlewares.AntiSpamCallbackMiddleware())
    dp.callback_query.middleware(middlewares.IgnoreMessageNotModifiedMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())
    dp.message.middleware(middlewares.MessageTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# Функции-обработчики команд из importlib (нельзя использовать в других файлах из-за зацикливания)


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
    inviter = db.get_inviter(user_id)
    user_info = (f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                 f"ID: <code>{user_id}</code>\n"
                 f"Username: @{msg.from_user.username}\n"
                 f"Пригласил: <code>{inviter if inviter else 'Никто'}</code>\n"
                 f"Тип пользователя: {db.get_user_type(user_id)}")
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=topic_id, text=user_info, reply_markup=kb.admin_menu, parse_mode="HTML")
    db.set_tracking(msg.from_user.id, False)
    logging.info(f'Создан топик имени {user_id} @{msg.from_user.username}')


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
    logging.warning(f'Юзверь {msg.from_user.id} @{msg.from_user.username} просит помощи админа')


async def send_to_user(msg: Message) -> None:
    await bot.send_message(db.get_user_id(msg.message_thread_id), text=msg.text)


async def get_file(msg: Document):
    """Ловит документы и заменяет файл с расписанием schedule.db на полученный."""
    file_id = msg.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = await bot.download_file(file_path)
    if '.db' in os.path.basename(file_path):
        existing_file = 'data/schedule.db'
        os.remove(existing_file)
        destination = 'data/schedule.db'
        with open(destination, 'wb') as new_file:
            new_file.write(downloaded_file.read())
        logging.info('Заменили расписание')
    else:
        logging.info('Скинули не тот файл расписания')


async def send_custom_message(user_id: int, text: str):
    """Отправляет пользователю кастомное сообщение."""
    await bot.send_message(user_id, text)


async def broadcast(msg: Message) -> None:
    """Отправляет сообщение всем пользователям, не заблокировавшим бота."""
    await db.broadcast_message(bot, msg.text)
    logging.info('Отправлено сообщение всем пользователям')


async def send_callback(callback: Message) -> None:
    """Отправляет сообщение в личный топик пользователя при нажатии на инлайн кнопку."""
    if db.get_tracking(callback.from_user.id):
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=db.get_topic_id(callback.from_user.id),
                               text=callback.data)


async def send_user_status(event: ChatMemberUpdated, status: str) -> None:
    """Отправляет сообщение в админский чат о статусе пользователя (заблокировал или разблокировал бота)."""
    await bot.send_message(ADMIN_CHAT_ID, f"Пользователь @{event.from_user.username} {status} бота",
                           message_thread_id=db.get_topic_id(event.from_user.id))
