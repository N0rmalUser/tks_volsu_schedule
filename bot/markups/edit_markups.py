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

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import config
from bot.database.user import UserDatabase
from bot.markups import keyboard_factory


def get_editing_menu(schedule_id: int, week: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Время",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="День",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Неделя",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="week_edit",
            edit="2" if week == 1 else "1",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Преподаватель",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="teacher",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Группа",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="group",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Аудитория",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="room",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Тип занятия",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="lesson_type",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="delete",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def get_editing(user_id: int, schedule_ids: list, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    day = UserDatabase(user_id).day
    for i in schedule_ids:
        builder.button(
            text=str(i),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="lesson", schedule_id=i, value=value, keyboard_type=keyboard_type
            ),
        )
    builder.adjust(2)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.extend([1, 1])
    builder.button(
        text="📝 Добавить",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="add_new", day=day, value=value, keyboard_type=keyboard_type
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="cancel", day=day, value=value, keyboard_type=keyboard_type
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_new_lesson(user_id: int, value: int, keyboard_type: str):
    # TODO: Сделать добавление новых занятий
    day = UserDatabase(user_id).day
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="cancel", day=day, value=value, keyboard_type=keyboard_type
        ),
    )


def add_time(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    times = ["08:30", "10:10", "12:00", "13:40", "15:20", "17:00", "18:40"]
    for i in times:
        builder.button(
            text=i,
            callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
                action="add_new_day",
                add=str(times.index(i)),
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(4)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_day(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
    for i in days:
        builder.button(
            text=i,
            callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
                action="add_new_week",
                add=str(days.index(i) + 1),
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_week(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Числитель",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_type",
            add="1",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Знаменатель",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_type",
            add="2",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(1)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_day",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_lesson_type(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Лекция",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_lesson",
            add="л",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Практика",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_lesson",
            add="пр",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Лабораторная",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_lesson",
            add="лаб",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Курсовой проект",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="add_new_lesson",
            add="курс",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_week",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_lesson(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    builder.adjust(4)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_type",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_group(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    for group in config.GROUPS:
        builder.button(
            text=group,
            callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
                action="add_new_teacher",
                add=group,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_lesson",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_teacher(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    for teacher in config.TEACHERS:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
                action="add_new_room",
                add=teacher,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )

    builder.adjust(2)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_group",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_room(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    for room in config.ROOMS:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
                action="add_new_end",
                add=room,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(2)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
            previous="add_new_teacher",
        ),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=keyboard_factory.ScheduleConstructorCallbackFactory(
            action="cancel",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_time(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    times = ["08:30", "10:10", "12:00", "13:40", "15:20", "17:00", "18:40"]
    for i in times:
        builder.button(
            text=i,
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="time_edit",
                edit=str(times.index(i)),
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(4)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_day(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
    for i in days:
        builder.button(
            text=i,
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="day",
                day=days.index(i) + 1,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(3)
    return builder.as_markup()


def edit_week(schedule_id: int, week: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    if week == 1:
        builder.button(
            text="Знаменатель",
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="week_edit",
                edit="2",
                schedule_id=schedule_id,
                value=value,
                keyboard_type=keyboard_type,
            ),
        )
    else:
        builder.button(
            text="Числитель",
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="week_edit",
                edit="1",
                schedule_id=schedule_id,
                value=value,
                keyboard_type=keyboard_type,
            ),
        )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            edit="1",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(1)
    return builder.as_markup()


def edit_teacher(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()

    for teacher in config.TEACHERS:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="teacher_edit",
                edit=teacher,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )

    builder.adjust(2)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.extend([1, 1])
    # TODO: Добавить кнопку "Другой"
    builder.button(
        text="✏️ Другой",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="custom_teacher",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_group(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    for group in config.GROUPS:
        builder.button(
            text=group,
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="group_edit",
                edit=group,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.extend([1, 1])
    # TODO: Добавить кнопку "Другая"
    builder.button(
        text="✏️ Другая",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="custom_group",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_room(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    for room in config.ROOMS:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="room_edit",
                edit=room,
                value=value,
                schedule_id=schedule_id,
                keyboard_type=keyboard_type,
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.extend([1, 1])
    # TODO: Добавить кнопку "Другая"
    builder.button(
        text="✏️ Другая",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="custom_room",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_lesson(schedule_id: int, value: int, keyboard_type: str):
    pass


def edit_lesson_type(schedule_id: int, value: int, keyboard_type: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Лекция",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit",
            edit="л",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Практика",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit",
            edit="пр",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Лабораторная",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit",
            edit="лаб",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.button(
        text="Курсовой проект",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit",
            edit="курс",
            schedule_id=schedule_id,
            value=value,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="⬅️ Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back",
            value=value,
            schedule_id=schedule_id,
            keyboard_type=keyboard_type,
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()
