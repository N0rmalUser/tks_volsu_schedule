from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from data import utils
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import text_maker
import asyncio
import logging
import kb

bot = Bot(token="6345780201:AAEdrv7OPmEYFYbOnjW8taXELLmKfksfF7M")
dp = Dispatcher(storage=MemoryStorage())


async def main():
    utils.open_files()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


@dp.message(Command("start"))
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    utils.set_today_date(user_id)
    utils.set_week(user_id, "0")
    user_type = utils.get_user_type(user_id)
    args = msg.text.split()

    if len(args) > 1 and args[1] == "0L3QtSDQu":
        user_type = "teacher"
    utils.set_user_type(user_id, user_type)

    menu, keyboard = (kb.teacher_menu, kb.teachers) if user_type == "teacher" else (kb.student_menu, kb.groups)
    greeting = f'Привет, {msg.from_user.full_name}\n'
    if user_type == "teacher":
        greeting += f'Вот ссылка для приглашения преподавателей: https://t.me/tks_schedule_bot?start=0L3QtSDQu'
        await msg.answer(greeting, reply_markup=menu)
        await msg.answer("Выбери себя в списке", reply_markup=keyboard)
    else:
        await msg.answer(greeting, reply_markup=menu)
        await msg.answer("Выбери свою группу", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("ignore"))
async def ignore_handler(callback: CallbackQuery):
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("week-") or c.data.startswith("day/"))
async def combined_handler(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
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
        kb0, kb1 = kb.teacher_week0, kb.teacher_week1
    elif callback_type == "group":
        text = text_maker.get_group_schedule(user_id)
        kb0, kb1 = kb.group_week0, kb.group_week1
    elif callback_type == "room":
        text = text_maker.get_room_schedule(user_id)
        kb0, kb1 = kb.room_week0, kb.room_week1
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if utils.get_week(user_id) == "0":
        await callback.message.edit_text(text, reply_markup=kb0)
    elif utils.get_week(user_id) == "1":
        await callback.message.edit_text(text, reply_markup=kb1)
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("room-") or c.data.startswith("teacher-") or c.data.startswith("group-"))
async def unified_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    utils.set_today_date(user_id)
    data_parts = callback.data.split('-')
    callback_type = data_parts[0]
    entity_id = "-".join(data_parts[1:])
    if callback_type == "room":
        utils.set_room(user_id, entity_id)
        text = text_maker.get_room_schedule(user_id)
        week_kb0, week_kb1 = kb.room_week0, kb.room_week1
    elif callback_type == "teacher":
        utils.set_teacher(user_id, entity_id)
        text = text_maker.get_teacher_schedule(user_id)
        week_kb0, week_kb1 = kb.teacher_week0, kb.teacher_week1
    elif callback_type == "group":
        utils.set_group(user_id, entity_id)
        text = text_maker.get_group_schedule(user_id)
        week_kb0, week_kb1 = kb.group_week0, kb.group_week1
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if utils.get_week(user_id) == "0":
        await callback.message.edit_text(text, reply_markup=week_kb0)
    elif utils.get_week(user_id) == "1":
        await callback.message.edit_text(text, reply_markup=week_kb1)
    await callback.answer()


@dp.message()
async def _handler(msg: Message):
    user_id = msg.from_user.id
    user_type = utils.get_user_type(user_id)

    if msg.text == "Расписание на сегодня":
        utils.set_today_date(user_id)
        entity_id = utils.get_teacher(user_id) if user_type == "teacher" else utils.get_group(user_id)

        if not entity_id:
            await bot.send_message(user_id, f"Сначала выберите {'ФИО преподавателя' if user_type == 'teacher' else 'группу'}, нажав на соответствующую кнопку.")
            return

        week_kb = kb.teacher_week0 if utils.get_week(user_id) == "0" else kb.teacher_week1
        await bot.send_message(user_id, text_maker.get_teacher_schedule(user_id), reply_markup=week_kb)
    elif msg.text == "Кабинеты":
        await bot.send_message(user_id, f"Выберите кабинет", reply_markup=kb.rooms)
    elif msg.text == "Группы":
        await bot.send_message(user_id, f"Выберите группу", reply_markup=kb.groups)
    elif msg.text == "Преподаватели":
        await bot.send_message(user_id, f"Выберите преподавателя", reply_markup=kb.teachers)


if __name__ == "__main__":
    utils.init_db()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
