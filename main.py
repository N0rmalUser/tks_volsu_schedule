from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from datetime import datetime
import image_maker
import json
import asyncio
import logging

import text_maker
from data import config
import utils
import kb

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


@dp.message(Command("start"))
async def start_handler(msg: Message):
    text_parts = msg.text.split()
    utils.week[msg.from_user.id] = "0"
    if len(text_parts) > 1:
        if text_parts[1] == "1337":
            utils.user[msg.from_user.id] = "teacher"
            await msg.answer(f'Привет, {msg.from_user.full_name}\nВот ссылка для приглашения преподавателей: '
                             f'https://t.me/tks_schedule_bot?start=1337', reply_markup=kb.teacher_menu)
            await msg.answer(f"Выбери себя в списке", reply_markup=kb.teachers)
        else:
            utils.user[msg.from_user.id] = "student"
            await msg.answer(f"Ломай, ломай! Мы же миллионеры!", reply_markup=kb.student_menu)
    else:
        utils.user[msg.from_user.id] = "student"
        await msg.answer(f'Привет, {msg.from_user.full_name}\n', reply_markup=kb.student_menu)
        await msg.answer(f"Выбери свою группу", reply_markup=kb.groups)
    utils.set_view_setting(msg.from_user.id, "text")


@dp.callback_query(lambda c: c.data.startswith("ignore"))
async def ignore_handler(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("week-"))
async def week_handler(callback: types.CallbackQuery):
    callback_type = callback.data.split('-')[1]
    week = callback.data.split('-')[2]
    user_id = callback.from_user.id
    utils.week[callback.from_user.id] = week
    if callback_type == "teacher":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_teacher_image(week, utils.day[user_id], utils.teacher[user_id])
            teacher_photo = FSInputFile("images\\teacher_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=teacher_photo),
                                                  reply_markup=kb.teacher_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=teacher_photo),
                                                  reply_markup=kb.teacher_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_teacher_schedule(week, utils.day[user_id], utils.teacher[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.teacher_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.teacher_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.message.edit_text("Ошибка #004. Напишите админу")
    elif callback_type == "group":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_group_image(week, utils.day[user_id], utils.group[user_id])
            group_photo = FSInputFile("images\\group_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=group_photo),
                                                  reply_markup=kb.group_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=group_photo),
                                                  reply_markup=kb.group_week1)
            else:
                await callback.message.edit_text("Ошибка #002. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_group_schedule(week, utils.day[user_id], utils.group[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.group_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.group_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.message.edit_text("Ошибка #004. Напишите админу")
    elif callback_type == "room":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_room_image(week, utils.day[user_id], utils.room[user_id])
            room_photo = FSInputFile("images\\room_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=room_photo),
                                                  reply_markup=kb.teacher_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=room_photo),
                                                  reply_markup=kb.teacher_week1)
            else:
                await callback.message.edit_text("Ошибка #003. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_room_schedule(week, utils.day[user_id], utils.room[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.room_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.room_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.message.edit_text("Ошибка #004. Напишите админу")
    else:
        await callback.message.edit_text("Ошибка #007. Напишите админу")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("day/"))
async def day_handler(callback: types.CallbackQuery):
    callback_type = callback.data.split('/')[1]
    week = callback.data.split('/')[2]
    day = callback.data.split('/')[3]
    user_id = callback.from_user.id
    utils.day[user_id] = day
    if callback_type == "teacher":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_teacher_image(week, day, utils.teacher[user_id])
            teacher_photo = FSInputFile("images\\teacher_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=teacher_photo),
                                                  reply_markup=kb.teacher_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=teacher_photo),
                                                  reply_markup=kb.teacher_week1)
            else:
                await callback.message.edit_text("Ошибка #008. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_teacher_schedule(week, day, utils.teacher[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.teacher_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.teacher_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.answer("Ошибка #009. Напишите админу")
    elif callback_type == "group":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_group_image(week, utils.day[user_id], utils.group[user_id])
            group_photo = FSInputFile("images\\group_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=group_photo),
                                                  reply_markup=kb.group_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=group_photo),
                                                  reply_markup=kb.group_week1)
            else:
                await callback.answer("Ошибка #010. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_group_schedule(week, day, utils.group[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.group_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.group_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.answer("Ошибка #009. Напишите админу")
    elif callback_type == "room":
        if utils.get_view_setting(user_id) == "image":
            image_maker.get_room_image(week, utils.day[user_id], utils.room[user_id])
            room_photo = FSInputFile("images\\room_schedule.png")
            if week == "0":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=room_photo),
                                                  reply_markup=kb.room_week0)
            elif week == "1":
                await callback.message.edit_media(media=types.InputMediaPhoto(media=room_photo),
                                                  reply_markup=kb.room_week1)
            else:
                await callback.answer("Ошибка #011. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            text = text_maker.get_room_schedule(week, day, utils.room[user_id])
            if week == "0":
                await callback.message.edit_text(text, reply_markup=kb.room_week0)
            elif week == "1":
                await callback.message.edit_text(text, reply_markup=kb.room_week1)
            else:
                await callback.message.edit_text("Ошибка #001. Напишите админу")
        else:
            await callback.answer("Ошибка #009. Напишите админу")
    else:
        await callback.message.edit_text("Ошибка #015. Напишите админу")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("room-"))
async def room_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    utils.day[user_id] = f'{datetime.now().weekday() + 1}'
    utils.week[user_id] = "1" if datetime.now().isocalendar()[1] % 2 == 0 else "0"
    utils.room[user_id] = callback.data.split('-')[1] + "-" + callback.data.split('-')[2]
    if utils.get_view_setting(user_id) == "image":
        image_maker.get_room_image(utils.week[user_id], utils.day[user_id], utils.room[user_id])
        room_photo = FSInputFile("images\\room_schedule.png")
        if utils.message_counter[user_id] is not None:
            msg = await bot.send_message(user_id, f"Подождите ...")
            await bot.delete_message(chat_id=user_id, message_id=msg.message_id - 1)
            await bot.delete_message(chat_id=user_id, message_id=msg.message_id)
        if utils.week[user_id] == "0":
            await bot.send_photo(user_id, room_photo, reply_markup=kb.room_week0)
        elif utils.week[user_id] == "1":
            await bot.send_photo(user_id, room_photo, reply_markup=kb.room_week1)
        else:
            await bot.send_message(user_id, f"Какая-то ошибка. Напишите админу")
        utils.message_counter[user_id] = 1
    elif utils.get_view_setting(user_id) == "text":
        text = text_maker.get_room_schedule(utils.week[user_id], utils.day[user_id], utils.room[user_id])
        if utils.message_counter[user_id] is not None:
            msg = await bot.send_message(user_id, f"Подождите ...")
            await bot.delete_message(chat_id=user_id, message_id=msg.message_id - 1)
            await bot.delete_message(chat_id=user_id, message_id=msg.message_id)
        if utils.week[user_id] == "0":
            await bot.send_message(user_id, text, reply_markup=kb.room_week0)
        elif utils.week[user_id] == "1":
            await bot.send_message(user_id, text, reply_markup=kb.room_week1)
        else:
            await bot.send_message(user_id, f"Какая-то ошибка. Напишите админу")

    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("teacher-"))
async def teacher_handler(callback: types.CallbackQuery):
    teacher = callback.data.split('-')[1]
    user_id = callback.from_user.id
    utils.day[user_id] = f'{datetime.now().weekday() + 1}'
    utils.week[user_id] = "1" if datetime.now().isocalendar()[1] % 2 == 0 else "0"
    utils.teacher[user_id] = teacher
    if utils.get_view_setting(user_id) == "image":
        image_maker.get_teacher_image(utils.week[user_id], utils.day[user_id], teacher)
        teacher_photo = FSInputFile("images\\teacher_schedule.png")
        if utils.week[user_id] == "0":
            await bot.send_photo(user_id, teacher_photo, reply_markup=kb.teacher_week0)
            await callback.message.delete()
        elif utils.week[user_id] == "1":
            await bot.send_photo(user_id, teacher_photo, reply_markup=kb.teacher_week1)
            await callback.message.delete()
        else:
            await callback.message.edit_text("Какая-то ошибка. Напишите админу")
    elif utils.get_view_setting(user_id) == "text":
        text = text_maker.get_teacher_schedule(utils.week[user_id], utils.day[user_id], teacher)
        if utils.week[user_id] == "0":
            await bot.send_message(user_id, text, reply_markup=kb.teacher_week0)
            await callback.message.delete()
        elif utils.week[user_id] == "1":
            await bot.send_message(user_id, text, reply_markup=kb.teacher_week1)
            await callback.message.delete()
        else:
            await callback.message.edit_text("Какая-то ошибка. Напишите админу")
    else:
        await callback.message.edit_text("Ошибка #004. Напишите админу")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("group-"))
async def group_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    utils.day[user_id] = f'{datetime.now().weekday() + 1}'
    utils.week[user_id] = "1" if datetime.now().isocalendar()[1] % 2 == 0 else "0"
    group = callback.data.split('-')[1] + "-" + callback.data.split('-')[2]
    utils.group[user_id] = group
    if utils.get_view_setting(user_id) == "image":
        image_maker.get_group_image(utils.week[user_id], utils.day[user_id], group)
        group_photo = FSInputFile("images\\group_schedule.png")
        if utils.week[user_id] == "0":
            await bot.send_photo(user_id, group_photo, reply_markup=kb.group_week0)
            await callback.message.delete()
        elif utils.week[user_id] == "1":
            await bot.send_photo(user_id, group_photo, reply_markup=kb.group_week1)
            await callback.message.delete()
        else:
            await callback.message.edit_text("Какая-то ошибка. Напишите админу")
    elif utils.get_view_setting(user_id) == "text":
        text = text_maker.get_group_schedule(utils.week[user_id], utils.day[user_id], group)
        if utils.week[user_id] == "0":
            await bot.send_message(user_id, text, reply_markup=kb.group_week0)
            await callback.message.delete()
        elif utils.week[user_id] == "1":
            await bot.send_message(user_id, text, reply_markup=kb.group_week1)
            await callback.message.delete()
        else:
            await callback.message.edit_text("Какая-то ошибка. Напишите админу")
    else:
        await callback.answer("Ошибка #009. Напишите админу")

    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("view_"))
async def view_handler(callback: types.CallbackQuery):
    if callback.data == "view_image":
        utils.set_view_setting(callback.from_user.id, "image")
    elif callback.data == "view_text":
        utils.set_view_setting(callback.from_user.id, "text")
    await callback.answer()
    await callback.message.edit_text(f"Оформление изменено на {'текст' if utils.get_view_setting(callback.from_user.id) != 'image' else 'картинки'}")


@dp.message()
async def _handler(msg: Message):
    user_id = msg.from_user.id
    utils.message_counter[user_id] = None
    if msg.text == "Расписание на сегодня":
        utils.day[user_id] = f'{datetime.now().weekday() + 1}'
        utils.week[user_id] = "1" if datetime.now().isocalendar()[1] % 2 == 0 else "0"
        if utils.get_view_setting(user_id) == "image":
            if utils.user[user_id] == "teacher":
                image_maker.get_teacher_image(utils.week[user_id], utils.day[user_id], utils.teacher[user_id])
                teacher_photo = FSInputFile("images\\teacher_schedule.png")
                if utils.week[user_id] == "0":
                    await bot.send_photo(user_id, teacher_photo, reply_markup=kb.teacher_week0)
                elif utils.week[user_id] == "1":
                    await bot.send_photo(user_id, teacher_photo, reply_markup=kb.teacher_week1)
                else:
                    await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
            elif utils.user[user_id] == "student":
                image_maker.get_group_image(utils.week[user_id], utils.day[user_id], utils.group[user_id])
                group_photo = FSInputFile("images\\group_schedule.png")
                if utils.week[user_id] == "0":
                    await bot.send_photo(user_id, group_photo, reply_markup=kb.group_week0)
                elif utils.week[user_id] == "1":
                    await bot.send_photo(user_id, group_photo, reply_markup=kb.group_week1)
                else:
                    await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
            else:
                await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
        elif utils.get_view_setting(user_id) == "text":
            if utils.user[user_id] == "teacher":
                text = text_maker.get_teacher_schedule(utils.week[user_id], utils.day[user_id], utils.teacher[user_id])
                if utils.week[user_id] == "0":
                    await bot.send_message(user_id, text, reply_markup=kb.teacher_week0)
                elif utils.week[user_id] == "1":
                    await bot.send_message(user_id, text, reply_markup=kb.teacher_week1)
                else:
                    await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
            elif utils.user[user_id] == "student":
                text = text_maker.get_teacher_schedule(utils.week[user_id], utils.day[user_id], utils.teacher[user_id])
                if utils.week[user_id] == "0":
                    await bot.send_message(user_id, text, reply_markup=kb.group_week0)
                elif utils.week[user_id] == "1":
                    await bot.send_message(user_id, text, reply_markup=kb.group_week1)
                else:
                    await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
            else:
                await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")
        else:
            await bot.send_message(user_id, "Какая-то ошибка. Напишите админу")

    elif msg.text == "Изменить оформление":
        await bot.send_message(user_id, f"Выберите оформление", reply_markup=kb.view)
    elif msg.text == "Кабинеты":
        await bot.send_message(user_id, f"Выберите кабинет", reply_markup=kb.rooms)
    elif msg.text == "Группы":
        await bot.send_message(user_id, f"Выберите группу", reply_markup=kb.groups)
    elif msg.text == "Преподаватели":
        await bot.send_message(user_id, f"Выберите преподавателя", reply_markup=kb.teachers)


if __name__ == "__main__":
    utils.open_files()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
