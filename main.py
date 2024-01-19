from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aioUtils import ChatTypeFilter, AntiSpamMiddleware

import asyncio

from data.config import BOT_TOKEN, GROUP_CHAT_ID, TEACHER_KEY

import kb

import logging

import text_maker

import utils


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(AntiSpamMiddleware())


async def main():
    utils.open_files()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def topic_create(msg: Message):
    user_id = msg.from_user.id
    if utils.get_topic_id(user_id):
        return
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {user_id}"
    else:
        topic_name = f"{msg.from_user.full_name} {str(user_id)}"

    result = await bot.create_forum_topic(GROUP_CHAT_ID, topic_name)
    topic_id = result.message_thread_id
    utils.set_topic_id(user_id, topic_id)
    user_info = (f"Пользователь: {msg.from_user.full_name}\nID: {user_id}\nUsername: @{msg.from_user.username}\n"
                 f"Номер телефона: {msg.contact}\nПригласил: {utils.get_inviter(user_id) if utils.get_inviter(user_id) else 'Никто'}\n"
                 f"Тип пользователя: {utils.get_user_type(user_id)}")
    if utils.get_tracking(user_id):
        await bot.send_message(GROUP_CHAT_ID, message_thread_id=topic_id, text=user_info)


@dp.message(Command("start"), ChatTypeFilter(chat_type="private"))
async def _start_handler(msg: Message):
    user_id = int(msg.from_user.id)
    utils.set_last_date(msg)
    utils.set_today_date(user_id)
    utils.set_week(user_id, 1)
    user_type = utils.get_user_type(user_id)
    args = msg.text.split()
    if len(args) > 1 and len(args[1].split('=')) > 1 and args[1].split('=')[1] == TEACHER_KEY:
        user_type = "teacher"
    utils.set_user_type(msg, user_type)
    menu, keyboard = (kb.teacher_menu, kb.teachers) if user_type == "teacher" else (kb.student_menu, kb.groups)
    if user_type == "teacher":
        await msg.answer(f"Привет, {msg.from_user.full_name}\nВот ссылка для приглашения преподавателей: https://t.me/tks_schedule_bot?start={user_id}={TEACHER_KEY}", reply_markup=menu)
        await msg.answer("Выбери себя в списке", reply_markup=keyboard)
    else:
        utils.set_user_type(msg, "student")
        await msg.answer(f'Привет, {msg.from_user.full_name}\nВот ссылка для приглашения: https://t.me/tks_schedule_bot?start={user_id}', reply_markup=menu)
        await msg.answer("Выбери свою группу", reply_markup=keyboard)
    utils.set_inviter(user_id, int(args[1].split('=')[0]) if len(args) > 1 else None)
    await topic_create(msg)
    if utils.get_tracking(user_id):
        await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(user_id), text=msg.text)


@dp.message(Command("admin"), ChatTypeFilter(chat_type="private"))
async def _admin_handler(msg: Message):
    await bot.send_message(msg.from_user.id, "Модератор скоро напишет вам, ожидайте")
    if utils.get_tracking(msg.from_user.id):
        await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(msg.from_user.id), text="Юзверь просит помощи админа @n0rmal_user")


@dp.message(Command("schedule_update"), ChatTypeFilter(chat_type="private"))
async def _schedule_update_handler(msg: Message):
    wait_msg = await bot.send_message(msg.from_user.id, "Сейчас обновиться, подождите")
    utils.open_files()
    await wait_msg.delete()
    await bot.send_message(msg.from_user.id, "Ура! Обновили расписание")


@dp.callback_query(lambda c: c.data.startswith("ignore"))
async def _ignore_handler(callback: CallbackQuery):
    await callback.answer("Сейчас эта неделя")


@dp.callback_query(lambda c: c.data.startswith("week-") or c.data.startswith("day/"))
async def _week_day_handler(callback: CallbackQuery):
    data = callback.data
    user_id = int(callback.from_user.id)
    if data.startswith("week-"):
        _, callback_type, week = data.split('-')
        day = utils.get_day(user_id)
        utils.set_week(user_id, week)
    elif data.startswith("day/"):
        _, callback_type, week, day = data.split('/')
        if day == utils.get_day(user_id):
            await callback.answer()
            return
    else:
        await callback.answer("Неизвестный тип запроса.")
        return
    utils.set_day(user_id, day)
    utils.set_week(user_id, week)

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

    if utils.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=kb1)
    elif utils.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=kb2)
    if utils.get_tracking(user_id):
        await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(callback.from_user.id), text=callback.data)
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("room-") or c.data.startswith("teacher-") or c.data.startswith("group-"))
async def _room_teacher_group_handler(callback: CallbackQuery):
    user_id = int(callback.from_user.id)
    utils.set_today_date(user_id)
    data_parts = callback.data.split('-')
    callback_type = data_parts[0]
    entity_id = "-".join(data_parts[1:])
    if callback_type == "room":
        utils.set_room(user_id, entity_id)
        text = text_maker.get_room_schedule(user_id)
        week_kb1, week_kb2 = kb.room_week1, kb.room_week2
    elif callback_type == "teacher":
        utils.set_teacher(user_id, entity_id)
        text = text_maker.get_teacher_schedule(user_id)
        week_kb1, week_kb2 = kb.teacher_week1, kb.teacher_week2
    elif callback_type == "group":
        utils.set_group(user_id, entity_id)
        text = text_maker.get_group_schedule(user_id)
        week_kb1, week_kb2 = kb.group_week1, kb.group_week2
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if utils.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=week_kb1)
    elif utils.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=week_kb2)
    if utils.get_tracking(user_id):
        await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(callback.from_user.id), text=callback.data)
    await callback.answer()


@dp.message(ChatTypeFilter(chat_type="private"))
async def _handler(msg: Message):
    user_id = msg.from_user.id
    user_type = utils.get_user_type(user_id)
    if msg.content_type == "text":
        if msg.text == "Расписание на сегодня":
            utils.set_today_date(user_id)
            entity_id = utils.get_teacher(user_id) if user_type == "teacher" else utils.get_group(user_id)

            if not entity_id:
                await bot.send_message(user_id, f"Сначала выберите {'ФИО преподавателя' if user_type == 'teacher' else 'группу'}, нажав на соответствующую кнопку.")
                return
            week_kb = kb.teacher_week1 if utils.get_week(user_id) == 1 else kb.teacher_week2
            await bot.send_message(user_id, text_maker.get_teacher_schedule(user_id), reply_markup=week_kb)
        elif msg.text == "Кабинеты":
            await bot.send_message(user_id, f"Выберите кабинет", reply_markup=kb.rooms)
        elif msg.text == "Группы":
            await bot.send_message(user_id, f"Выберите группу", reply_markup=kb.groups)
        elif msg.text == "Преподаватели":
            await bot.send_message(user_id, f"Выберите преподавателя", reply_markup=kb.teachers)
        if utils.get_tracking(user_id):
            await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(msg.from_user.id), text=msg.text)
    else:
        await bot.send_message(user_id, text="Я тебя не понимаю, буковы пиши!")
        if utils.get_tracking(user_id):
            await bot.send_message(GROUP_CHAT_ID, message_thread_id=utils.get_topic_id(msg.from_user.id), text="Пытался отправить не тектовое сообщение")
    utils.set_last_date(msg)


@dp.message(Command("track"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command(msg: Message):
    data = msg.text.split(' ')
    if msg.chat.id == GROUP_CHAT_ID and not msg.from_user.is_bot:
        if msg.message_thread_id:
            utils.set_tracking(msg, True if data[1] == "start" else False)


@dp.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_message(msg: Message):
    if msg.chat.id == GROUP_CHAT_ID and not msg.from_user.is_bot:
        if msg.message_thread_id:
            await bot.send_message(utils.get_user_id(msg.message_thread_id), text=msg.text)
        else:
            await utils.broadcast_message(bot, msg.text)


if __name__ == "__main__":
    utils.init_db()
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(main())
