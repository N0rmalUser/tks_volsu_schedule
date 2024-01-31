from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated, FSInputFile
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aioUtils import ChatTypeFilter, AntiSpamMessageMiddleware, AntiSpamCallbackMiddleware, \
    IgnoreMessageNotModifiedMiddleware

import asyncio

from data.config import BOT_TOKEN, ADMIN_CHAT_ID, LOG_FILE, DB_PATH

import dbUtils

import kb

import logging

import text_maker

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main() -> None:
    """Bot launch function. Open schedule file. Delete webhook. Start polling."""
    dp.message.middleware(AntiSpamMessageMiddleware())
    dp.callback_query.middleware(AntiSpamCallbackMiddleware())
    dp.callback_query.middleware(IgnoreMessageNotModifiedMiddleware())
    dbUtils.open_schedule_file()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def topic_create(msg: Message) -> None:
    """Create topic for user tracking and send user info. Set topic id. If user already has topic, do nothing."""
    user_id = msg.from_user.id
    if dbUtils.get_topic_id(user_id):
        return
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {user_id}"
    else:
        topic_name = f"{msg.from_user.full_name} {str(user_id)}"

    result = await bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
    topic_id = result.message_thread_id
    dbUtils.set_topic_id(user_id, topic_id)
    user_info = (f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
                 f"ID: <code>{user_id}</code>\n"
                 f"Username: @{msg.from_user.username}\n"
                 f"Номер телефона: {msg.contact}\n"
                 f"Пригласил: <code>{dbUtils.get_inviter(user_id) if dbUtils.get_inviter(user_id) else 'Никто'}</code>\n"
                 f"Тип пользователя: {dbUtils.get_user_type(user_id)}")
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=topic_id, text=user_info, reply_markup=kb.admin_menu, parse_mode="HTML")
    dbUtils.set_tracking(msg.from_user.id, False)


@dp.message(CommandStart(deep_link=True))
async def _start_deep_handler(msg: Message, command: CommandObject) -> None:
    """/Start command handler in private chat. Create topic for user tracking. Send invite link and menu. Set inviter id and user type."""
    try:
        payload = decode_payload(command.args)
        args = payload.split("=")
        user_id = int(msg.from_user.id)
        dbUtils.set_inviter(user_id, int(args[0]))
        if args[1] == "teacher":
            user_type = "teacher"
            menu, keyboard = kb.teacher_menu, kb.teachers
        else:
            user_type = "student"
            menu, keyboard = kb.student_menu, kb.groups
        dbUtils.set_last_date(msg)
        dbUtils.set_today_date(user_id)
        dbUtils.set_week(user_id, 1)
        dbUtils.set_user_type(msg, user_type)
        link = await create_start_link(bot, f"{user_id}={dbUtils.get_user_type(user_id)}", encode=True)
        await msg.answer(f"Привет, {msg.from_user.full_name}\n"
                         f"Вот ссылка для приглашения: {link}",
                         reply_markup=menu)
        await msg.answer("Выбери себя в списке", reply_markup=keyboard)
        await topic_create(msg)
    except Exception:
        await msg.answer("Неверная ссылка")


@dp.message(CommandStart())
async def _start_handler(msg: Message) -> None:
    user_id = int(msg.from_user.id)
    dbUtils.set_last_date(msg)
    dbUtils.set_today_date(user_id)
    dbUtils.set_week(user_id, 1)
    user_type = dbUtils.get_user_type(user_id)
    dbUtils.set_user_type(msg, user_type)
    menu, keyboard = (kb.teacher_menu, kb.teachers) if user_type == "teacher" else (
        kb.student_menu, kb.groups)
    link = await create_start_link(bot, f"{user_id}={dbUtils.get_user_type(user_id)}", encode=True)
    await msg.answer(f"Привет, {msg.from_user.full_name}\n"
                     f"Вот ссылка для приглашения: {link}",
                     reply_markup=menu)
    await msg.answer("Выбери себя в списке", reply_markup=keyboard)
    await topic_create(msg)


@dp.message(Command("admin"), ChatTypeFilter(chat_type="private"))
async def _admin_handler(msg: Message) -> None:
    """/admin command handler. Send message to admin chat. If user already has topic, send message to topic."""
    await bot.send_message(msg.from_user.id, "Модератор скоро напишет вам, ожидайте")
    await bot.send_message(ADMIN_CHAT_ID, message_thread_id=dbUtils.get_topic_id(msg.from_user.id),
                           text="Юзверь просит помощи админа @n0rmal_user")
    await bot.forward_message(ADMIN_CHAT_ID, from_chat_id=msg.chat.id, message_id=msg.message_id,
                              message_thread_id=dbUtils.get_topic_id(msg.from_user.id))
    dbUtils.set_tracking(dbUtils.get_user_id(msg.message_thread_id), True)


@dp.callback_query(lambda c: c.data.startswith("ignore"))
async def _ignore_handler(callback: CallbackQuery) -> None:
    """Ignore callback handler. Answer callback."""
    await callback.answer("Сейчас эта неделя")


@dp.callback_query(lambda c: c.data.startswith("week-") or c.data.startswith("day/"))
async def _week_day_handler(callback: CallbackQuery) -> None:
    """Week and day callback handler. Set week and day. Send schedule."""
    data = callback.data
    user_id = int(callback.from_user.id)
    if data.startswith("week-"):
        _, callback_type, week = data.split('-')
        day = dbUtils.get_day(user_id)
        dbUtils.set_week(user_id, week)
    elif data.startswith("day/"):
        _, callback_type, week, day = data.split('/')
        if day == dbUtils.get_day(user_id):
            await callback.answer()
            return
    else:
        await callback.answer("Неизвестный тип запроса.")
        return
    dbUtils.set_day(user_id, day)
    dbUtils.set_week(user_id, week)

    if callback_type == "teacher":
        text = text_maker.get_teacher_schedule(user_id)
        kb1, kb2 = kb.teacher_week1, kb.teacher_week2
    elif callback_type == "group":
        text = text_maker.get_group_schedule(user_id)
        kb1, kb2 = kb.group_week1, kb.group_week2
    elif callback_type == "room":
        text = text_maker.get_room_schedule(user_id)
        kb1, kb2 = kb.room_week1, kb.room_week2
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if dbUtils.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=kb1)
    elif dbUtils.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=kb2)
    if dbUtils.get_tracking(user_id):
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=dbUtils.get_topic_id(callback.from_user.id),
                               text=callback.data)
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("room-") or c.data.startswith("teacher-") or c.data.startswith("group-"))
async def _room_teacher_group_handler(callback: CallbackQuery) -> None:
    """Room, teacher and group callback handler. Set room, teacher or group and send schedule."""
    user_id = int(callback.from_user.id)
    dbUtils.set_today_date(user_id)
    data_parts = callback.data.split('-')
    callback_type = data_parts[0]
    entity_id = "-".join(data_parts[1:])
    if callback_type == "room":
        dbUtils.set_room(user_id, entity_id)
        text = text_maker.get_room_schedule(user_id)
        week_kb1, week_kb2 = kb.room_week1, kb.room_week2
    elif callback_type == "teacher":
        dbUtils.set_teacher(user_id, entity_id)
        text = text_maker.get_teacher_schedule(user_id)
        week_kb1, week_kb2 = kb.teacher_week1, kb.teacher_week2
    elif callback_type == "group":
        dbUtils.set_group(user_id, entity_id)
        text = text_maker.get_group_schedule(user_id)
        week_kb1, week_kb2 = kb.group_week1, kb.group_week2
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if dbUtils.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=week_kb1)
    elif dbUtils.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=week_kb2)
    if dbUtils.get_tracking(user_id):
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=dbUtils.get_topic_id(callback.from_user.id),
                               text=callback.data)
    await callback.answer()


@dp.message(ChatTypeFilter(chat_type="private"))
async def _handler(msg: Message) -> None:
    """Private chat message handler. Send schedule, rooms, teachers or groups."""
    user_id = msg.from_user.id
    user_type = dbUtils.get_user_type(user_id)
    if msg.content_type == "text":
        if msg.text == "Расписание на сегодня":
            dbUtils.set_today_date(user_id)
            entity_id = dbUtils.get_teacher(user_id) if user_type == "teacher" else dbUtils.get_group(user_id)

            if not entity_id:
                await msg.answer(
                    f"Сначала выберите {'ФИО преподавателя' if user_type == 'teacher' else 'группу'}, нажав на соответствующую кнопку.")
                return
            if user_type == "teacher":
                week_kb = kb.teacher_week1 if dbUtils.get_week(user_id) == 1 else kb.teacher_week2
                await msg.answer(text_maker.get_teacher_schedule(user_id), reply_markup=week_kb)
            elif user_type == "student":
                week_kb = kb.group_week1 if dbUtils.get_week(user_id) == 1 else kb.group_week2
                await msg.answer(text_maker.get_group_schedule(user_id), reply_markup=week_kb)
            else:
                await msg.answer("Ошибка! Напишите админу /admin")
        elif msg.text == "Кабинеты":
            await msg.answer(f"Выберите кабинет", reply_markup=kb.rooms)
        elif msg.text == "Группы":
            await msg.answer(f"Выберите группу", reply_markup=kb.groups)
        elif msg.text == "Преподаватели":
            await msg.answer(f"Выберите преподавателя", reply_markup=kb.teachers)
        if dbUtils.get_tracking(user_id):
            await bot.forward_message(ADMIN_CHAT_ID, from_chat_id=msg.chat.id, message_id=msg.message_id,
                                      message_thread_id=dbUtils.get_topic_id(msg.from_user.id))
    else:
        await bot.send_message(user_id, text="Я тебя не понимаю, буковы пиши!")
    dbUtils.set_last_date(msg)


@dp.message(Command("menu"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID:
        await msg.answer("Меню админа", reply_markup=kb.admin_menu)


@dp.message(Command("log"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        if command.args == 'send' or command.args == 'show':
            try:
                await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
            except:
                await msg.answer("В лог файле ничего нет(")
        elif command.args == 'clear' or command.args == 'del':
            open(LOG_FILE, 'w').write('')
            await msg.answer("Логи очищены")
        else:
            await msg.answer("Такой команды нету (аргумент не правильный)")


@dp.message(Command("send_db"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID:
        if msg.message_thread_id:
            await msg.answer_document(FSInputFile(DB_PATH), caption="Вот ваша база данных")


@dp.message(Command("schedule_update"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _schedule_update_handler(msg: Message) -> None:
    """/schedule_update command handler. Update schedule json file."""
    wait_msg = await bot.send_message(msg.from_user.id, "Сейчас обновиться, подождите")
    await asyncio.sleep(1)
    dbUtils.open_schedule_file()
    await wait_msg.delete()
    await msg.answer("Ура! Обновили schedules")


@dp.message(Command("track"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    """/track [start,stop,status] command handler. Set tracking for user topic."""
    if msg.chat.id == ADMIN_CHAT_ID:
        if command.args is None:
            await msg.answer(
                "Ошибка: не переданы аргументы"
            )
            return
        command = str(command.args).lower()
        if msg.message_thread_id:
            user_id = dbUtils.get_user_id(msg.message_thread_id)
            if command == "start":
                dbUtils.set_tracking(user_id, True)
            elif command == "stop":
                dbUtils.set_tracking(user_id, False)
            elif command == "status":
                pass
            await msg.answer(f"Трекинг {'включен' if dbUtils.get_tracking(user_id) else 'выключен'}")
        else:
            if command == "start":
                await dbUtils.tracking_manage(True)
            elif command == "stop":
                await dbUtils.tracking_manage(False)
            elif command == "status":
                users = await dbUtils.get_tracked_users()
                tracked = '\n'.join([str(user) for user in users])
                await msg.answer(f"Трекаются: \n" + tracked if users else "Никто не трекается",
                                 parse_mode='MarkdownV2')


@dp.message(Command("info"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_info(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        if msg.message_thread_id:
            await msg.answer(dbUtils.get_user_info(dbUtils.get_user_id(msg.message_thread_id)),
                             parse_mode="MarkdownV2")
        else:
            await msg.answer(dbUtils.get_all_users_info())


@dp.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_message(msg: Message) -> None:
    """Group chat message handler. Send message to users from topic. If topic name "General", send message to all users."""
    if msg.text[0] != '/':
        if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
            if msg.message_thread_id is not None:
                await bot.send_message(dbUtils.get_user_id(msg.message_thread_id), text=msg.text)
            else:
                await dbUtils.broadcast_message(bot, msg.text)
    else:
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")


@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED), ChatTypeFilter(chat_type="private"))
async def user_blocked_bot(event: ChatMemberUpdated):
    dbUtils.set_blocked(event.from_user.id, True)
    await bot.send_message(ADMIN_CHAT_ID, f"Пользователь @{event.from_user.username} заблокировал бота",
                           message_thread_id=dbUtils.get_topic_id(event.from_user.id))


@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER), ChatTypeFilter(chat_type="private"))
async def user_unblocked_bot(event: ChatMemberUpdated):
    dbUtils.set_blocked(event.from_user.id, False)
    await bot.send_message(ADMIN_CHAT_ID, f"Пользователь @{event.from_user.username} разблокировал бота",
                           message_thread_id=dbUtils.get_topic_id(event.from_user.id))


if __name__ == "__main__":
    dbUtils.init_db()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    asyncio.run(main())
# , filename=LOG_FILE