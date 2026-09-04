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

from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text

from app.core.config import config
from app.schemas.enums import WeekType


def group_menu() -> str:
    keyboard = Keyboard()
    keyboard.add(Text("Расписание на сегодня"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("Группы"))
    keyboard.add(Text("Преподаватели"))
    return keyboard.get_json()


def teacher_menu() -> str:
    keyboard = Keyboard()
    keyboard.add(Text("Расписание на сегодня"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("Группы"))
    keyboard.add(Text("Преподаватели"))
    keyboard.add(Text("Кабинеты"))
    return keyboard.get_json()


def days(keyboard_type: Keyboard, day: int, week: WeekType, value: int) -> str:
    keyboard = Keyboard(inline=True)

    days_list = [
        ("Пн", 1),
        ("Вт", 2),
        ("Ср", 3),
        ("Чт", 4),
        ("Пт", 5),
        ("Сб", 6),
    ]

    for index, (label, int_day) in enumerate(days_list, start=1):
        keyboard.add(
            Callback(
                label=label,
                payload={
                    "action": "day",
                    "keyboard_type": keyboard_type,
                    "day": int_day,
                    "week": week,
                    "value": value,
                },
            ),
        )

        if index % 3 == 0:
            keyboard.row()

    if week == WeekType.ODD:
        keyboard.add(
            Callback("✅ Числитель", {"action": "ignore"}),
            color=KeyboardButtonColor.POSITIVE,
        )
        keyboard.add(
            Callback(
                "Знаменатель ➡️",
                {
                    "action": "week",
                    "keyboard_type": keyboard_type,
                    "week": WeekType.EVEN,
                    "day": day,
                    "value": value,
                },
            ),
        )

    elif week == WeekType.EVEN:
        keyboard.add(
            Callback("✅ Знаменатель", {"action": "ignore"}),
            color=KeyboardButtonColor.POSITIVE,
        )
        keyboard.add(
            Callback(
                "Числитель ➡️",
                {
                    "action": "week",
                    "keyboard_type": keyboard_type,
                    "week": WeekType.ODD,
                    "day": day,
                    "value": value,
                },
            ),
        )
    else:
        keyboard.add(Callback("Неизвестная неделя", {"action": "ignore"}))
    return keyboard.get_json()


def rooms() -> str:
    keyboard = Keyboard(inline=True)

    for i, room in enumerate(config.rooms, start=1):
        keyboard.add(
            Callback(
                label=str(room),
                payload={
                    "action": "room",
                    "value": i,
                },
            ),
        )

        if i % 3 == 0:
            keyboard.row()

    return keyboard.get_json()


def get_directions_from_groups() -> list:
    directions = []
    for g in config.groups:
        dir_part = g.split("-", 1)[0].strip() if "-" in g else g.split()[0].strip()
        if dir_part and dir_part not in directions:
            directions.append(dir_part)
    return directions


def directions() -> str:
    keyboard = Keyboard(inline=True)
    directions = get_directions_from_groups()

    for i, direction in enumerate(directions, start=1):
        keyboard.add(
            Callback(
                label=direction,
                payload={"action": "select_direction", "direction": direction},
            ),
        )
        if i % 3 == 0:
            keyboard.row()

    return keyboard.get_json()


def groups(direction: str) -> str:
    keyboard = Keyboard(inline=True)

    filtered = [
        g
        for g in config.groups
        if g.upper().startswith(direction.upper() + "-") or g.upper().startswith(direction.upper())
    ]

    sorted_groups = sorted([group for group in config.groups if group != "-"])
    for i, group in enumerate(filtered):
        keyboard.add(
            Callback(
                label=group,
                payload={"action": "group", "value": sorted_groups.index(group) + 1},
            ),
        )
        if (i + 1) % 2 == 0:
            keyboard.row()
    return keyboard.get_json()


def teachers(page: int = 0) -> str:
    keyboard = Keyboard(inline=True)

    start = page * 8
    end = start + 8
    chunk = sorted(config.teachers)[start:end]

    for i, teacher in enumerate(chunk, start=1):
        i += page * 8
        keyboard.add(
            Callback(
                label=teacher,
                payload={
                    "action": "teacher",
                    "value": i,
                },
            ),
        )

        if i % 2 == 0:
            keyboard.row()

    keyboard.row()

    if page > 0:
        keyboard.add(
            Callback(
                "⬅️ Назад",
                {"action": "teachers_page", "page": page - 1},
            ),
        )

    if end < len(config.teachers):
        keyboard.add(
            Callback(
                "Вперёд ➡️",
                {"action": "teachers_page", "page": page + 1},
            ),
        )

    return keyboard.get_json()
