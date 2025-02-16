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

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.config import ADMIN_CHAT_ID
from app.database.user import User
from app.filters import ChatTypeIdFilter
from app.markups import user as kb

router = Router()


@router.message(CommandStart(deep_link=True), ChatTypeIdFilter(chat_type=["private"]))
async def start_deep_handler(msg: Message, command: CommandObject) -> None:
    """Обработчик команды /start с deep_link'ом. Назначает тип пользователя в зависимости от ссылки, а также добавляет id пригласившего пользователя в базу данных."""

    from aiogram.utils.deep_linking import decode_payload

    try:
        payload = decode_payload(command.args)
        args = payload.split("=")
        user = UserDatabase(msg.from_user.id)
        user.inviter = int(args[0])
        if args[1] == "teacher":
            user.user_type = "teacher"
            menu, keyboard = kb.teacher_menu(), kb.get_teachers()
        else:
            user.user_type = "student"
            menu, keyboard = kb.student_menu(), kb.get_groups()
        if user.start_date is None:
            user.username = f"@{msg.from_user.username}"
            user.fullname = msg.from_user.full_name
        user.set_today_date()
        user.week = 1
        user.tracking = False

        from app import start_message

        await start_message(msg, menu, keyboard)
    except Exception:
        logging.warning(f"{msg.from_user.id} перешёл по неверной ссылке")
        await msg.answer("Неверная ссылка")


@router.message(CommandStart(), ChatTypeIdFilter(chat_type=["private"]))
async def start_handler(msg: Message) -> None:
    """Обработчик команды /start без deep_link'а."""

    user = User(msg.from_user.id)
    if user.start_date is None:
        user.username = f"@{msg.from_user.username}"
        user.fullname = msg.from_user.full_name
    user.set_today_date()
    user.week = 1
    user.tracking = False
    menu, keyboard = (
        (kb.teacher_menu(), kb.get_teachers())
        if user.type == "teacher"
        else (kb.student_menu(), kb.get_groups())
    )

    from app import start_message

    await start_message(msg, menu, keyboard)


@router.message(Command("help"), ChatTypeIdFilter(chat_type=["private"]))
async def help_handler(msg: Message) -> None:
    """Обработчик команды /help. Отправляет сообщение с описанием бота."""
    if User(msg.from_user.id).type == "teacher":
        await msg.answer(
            """
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.

Если у группы номер `ИБТС-231_2` - это 2-я подгруппа, если `_2` отсутствует, то должно придти вся группа, либо первая подгруппа. Отдельно первая подгруппа ни как не обозначается!!!

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/изменениях в расписании используйте команду /admin и опишите проблему.
"""
        )
    else:
        await msg.answer(
            """
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранной группы.
Кнопка `Группы` открывает меню выбора групп

Если у группы номер `ИБТС-231_2` - это 2-я подгруппа, если `_2` отсутствует, первая

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/изменениях в расписании используйте команду /admin и опишите проблему.
Донаты принимаются вкусняшками в 1-19М
"""
        )


@router.message(Command("admin"), ChatTypeIdFilter(chat_type=["private"]))
async def admin_handler(msg: Message) -> None:
    """Обработчик команды /admin. Пересылает сообщение админу и включает слежку за действиями пользователя."""

    from app import process_track

    user = User(msg.from_user.id)
    user.tracking = True
    logging.warning(f"Юзверь {msg.from_user.id} @{msg.from_user.username} просит помощи админа")
    await process_track(user, text="Юзверь просит помощи админа!", bot=msg.bot)
    await msg.forward(chat_id=ADMIN_CHAT_ID, message_thread_id=user.topic_id)
    await msg.answer("Модератор скоро напишет вам, ожидайте. Пока можете описать проблему.")
    logging.info(f"{msg.from_user.id} написал админу")


@router.message(Command("spreadsheets"), ChatTypeIdFilter(chat_type=["private"]))
async def admin_handler(msg: Message) -> None:
    """Обработчик команды /spreadsheets. Присылает пользователю файл с расписанием выбранной группы/преподавателя"""

    await msg.answer(
        "Выберите, какой тип расписания вы хотите скачать.",
        reply_markup=kb.get_sheets(msg.from_user.id),
    )


@router.message(Command("default"), ChatTypeIdFilter(chat_type=["private"]))
async def default_handler(msg: Message) -> None:
    """Устанавливает пользователю преподавателя или группу по-умолчанию"""

    if User(msg.from_user.id).type == "teacher":
        await msg.answer("Выберите себя из списка", reply_markup=kb.get_default_teachers())
    else:
        await msg.answer("Выберите себя из списка", reply_markup=kb.get_default_groups())


@router.message(F.text == "Расписание на сегодня", ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    from app.database.schedule import Schedule
    from app.misc import text_maker

    user_id = msg.from_user.id
    user = User(user_id)
    default = user.default

    if default is None:
        entity_id = user.teacher if user.type == "teacher" else user.group
    else:
        entity_id = Schedule().get_teacher_id(default)

    if not entity_id:
        await msg.answer(
            f"Сначала выберите {'ФИО преподавателя' if user.type == 'teacher' else 'группу'}, нажав на соответствующую кнопку."
        )
        return
    if user.type == "teacher":
        week_kb = kb.get_days(user_id, "teacher", user.week, value=entity_id)
        await msg.answer(
            text_maker.get_teacher_schedule(
                day=user.day,
                week=user.week,
                teacher_name=Schedule().get_teacher_name(entity_id),
            ),
            reply_markup=week_kb,
        )
    elif user.type == "student":
        week_kb = kb.get_days(user_id, "group", user.week, value=entity_id)
        await msg.answer(
            text_maker.get_group_schedule(
                day=user.day,
                week=user.week,
                group_name=Schedule().get_group_name(entity_id),
            ),
            reply_markup=week_kb,
        )
    else:
        logging.info(f"{msg.from_user.id} неправильный тип пользователя")
        await msg.answer("Ошибка! Напишите админу /admin")


@router.message(F.text == "Кабинеты", ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    await msg.answer(f"Выберите кабинет", reply_markup=kb.get_rooms())


@router.message(F.text == "Группы", ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    await msg.answer(f"Выберите группу", reply_markup=kb.get_groups())


@router.message(F.text == "Преподаватели", ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    await msg.answer(f"Выберите преподавателя", reply_markup=kb.get_teachers())


@router.message(F.text, ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    await msg.answer(f"Выберите преподавателя", reply_markup=kb.get_teachers())
    logging.info(f"{msg.from_user.id} написал неправильную команду")
    await msg.answer("Я не знаю такой команды")


@router.message(ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    await msg.answer("Я тебя не понимаю, буковы пиши!")
