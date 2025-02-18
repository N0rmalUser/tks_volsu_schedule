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
from datetime import datetime

import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.markups import admin
from app.misc.states import BroadcastStates

from . import schedule_parser, sheets_maker, states, text_maker, user_activity
from ..config import TIMEZONE, NUMERATOR


def get_today() -> tuple[int, int]:
    """Метод для получения сегодняшнего дня и недели"""

    day = int(f"{datetime.now(pytz.timezone(TIMEZONE)).weekday() + 1}")
    week_int = 2 if NUMERATOR == 0 else 1
    week = (
        week_int
        if datetime.now(pytz.timezone(TIMEZONE)).isocalendar()[1] % 2 == 0
        else 3 - week_int
    )
    if day == 7:
        return 1, week + 1 if week == 1 else week - 1

    else:
        return day, week


def time_to_minutes(time_str: str) -> int:
    """Метод для перевода времени в минуты"""

    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """Метод для получения эмодзи часов с указанным временем времени"""

    hour = int(start_time.split(":")[0])
    if 8 <= hour < 10:
        return "🕣 "
    elif 10 <= hour < 12:
        return "🕙 "
    elif 12 <= hour < 13:
        return "🕛 "
    elif 13 <= hour < 14:
        return "🕜 "
    elif 14 <= hour < 16:
        return "🕞 "
    elif 16 <= hour < 18:
        return "🕔 "
    elif 18 <= hour < 20:
        return "🕡 "
    else:
        return "🕙 "


def get_lesson_label(subject: str) -> str:
    """Метод для получения типа пары по его сокращению"""

    if "пр" in subject.lower():
        return "Практика"
    elif "пр." in subject.lower():
        return "Практика"
    elif "лаб" in subject.lower():
        return "Лабораторные"
    elif "лаб." in subject.lower():
        return "Лабораторные"
    elif "л" in subject.lower():
        return "Лекция"
    elif "л." in subject.lower():
        return "Лекция"
    elif ("курс" or "кур/проект" or "кур/проек.") in subject.lower():
        return "Курсовой проект"
    else:
        return ""


def create_progress_bar(completed: int, total: int) -> str:
    total_blocks = 20
    filled_blocks = int((completed / total) * total_blocks)
    bar = "■" * filled_blocks + "□" * (total_blocks - filled_blocks)
    return f"[{bar}]"


async def send_broadcast_message(msg: Message, state: FSMContext, message_id: int, user_ids: list[int]):
    from asyncio import sleep
    from app.database.user import User

    user_ids = all_user_ids()
    sent_count = 0
    total_users = len(user_ids)
    try:
        for user_id in user_ids:
            if await state.get_state() == BroadcastStates.cancel_sending.state:
                await msg.edit_text(text="Отправка отменена")
                break
            if not User(user_id).blocked:
                try:
                    await msg.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=msg.chat.id,
                        message_id=message_id,
                    )
                    sent_count += 1
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                finally:
                    await msg.edit_text(
                        text=f"Отправлено {sent_count} из {total_users} сообщений\n{create_progress_bar(sent_count, total_users)}",
                        reply_markup=admin.cancel_sending(),
                    )
                    await sleep(1)
        logging.info("Отправлено сообщение всем пользователям")
        await msg.edit_text("Рассылка завершена!")
    except TypeError:
        await msg.edit_text("Ошибка при отправке сообщения")
