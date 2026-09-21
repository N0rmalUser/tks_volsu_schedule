from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text

from app.core.config import config
from app.core.enums import WeekType
from app.schemas.keyboard import keyboard_data


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
        room_id = keyboard_data.room_ids[room]
        keyboard.add(
            Callback(
                label=room,
                payload={
                    "action": "room",
                    "value": room_id,
                },
            ),
        )

        if i % 3 == 0:
            keyboard.row()

    return keyboard.get_json()


def get_directions_from_groups() -> list:
    _directions = []
    for g in config.groups:
        dir_part = g.split("-", 1)[0].strip() if "-" in g else g.split()[0].strip()
        if dir_part and dir_part not in _directions:
            _directions.append(dir_part)
    return _directions


def directions() -> str:
    _directions = get_directions_from_groups()
    keyboard = Keyboard(inline=True)

    for i, direction in enumerate(_directions, start=1):
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

    filtered = [g for g in config.groups if g.upper().startswith(direction.upper())]

    for group in filtered:
        if int(group[-1]) == 1:
            keyboard.row()
        group_id = keyboard_data.group_ids[group]
        keyboard.add(
            Callback(
                label=group,
                payload={"action": "group", "value": group_id},
            ),
        )
    return keyboard.get_json()


def teachers(page: int = 0) -> str:
    keyboard = Keyboard(inline=True)

    start = page * 8
    end = start + 8
    chunk = sorted(config.teachers, key=str)[start:end]

    for i, teacher in enumerate(chunk, start=1):
        teacher_id = keyboard_data.teacher_ids[teacher]
        keyboard.add(
            Callback(
                label=teacher,
                payload={
                    "action": "teacher",
                    "value": teacher_id,
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
