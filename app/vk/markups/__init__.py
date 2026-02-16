from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text

from app.config import GROUPS, ROOMS, TEACHERS
from app.database.schedule import Schedule


def menu() -> str:
    keyboard = Keyboard()
    keyboard.add(Text("Расписание на сегодня"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("Группы"))
    keyboard.add(Text("Преподаватели"))
    keyboard.add(Text("Кабинеты"))
    return keyboard.get_json()


def days(keyboard_type: str, day: int, week: int, value: int) -> str:
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
            )
        )

        if index % 3 == 0:
            keyboard.row()

    if week == 1:
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
                    "week": 2,
                    "day": day,
                    "value": value,
                },
            )
        )

    elif week == 2:
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
                    "week": 1,
                    "day": day,
                    "value": value,
                },
            )
        )
    else:
        keyboard.add(Callback("Неизвестная неделя", {"action": "ignore"}))
    print(keyboard.get_json())
    return keyboard.get_json()


def rooms() -> str:
    keyboard = Keyboard(inline=True)
    schedule = Schedule()

    for i, room in enumerate(ROOMS, start=1):
        keyboard.add(
            Callback(
                label=str(room),
                payload={
                    "action": "room",
                    "value": schedule.get_room_id(room),
                },
            )
        )

        if i % 3 == 0:
            keyboard.row()

    return keyboard.get_json()


def get_directions_from_groups() -> list:
    directions = []
    for g in GROUPS:
        if "-" in g:
            dir_part = g.split("-", 1)[0].strip()
        else:
            dir_part = g.split()[0].strip()
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
            )
        )
        if i % 3 == 0:
            keyboard.row()

    return keyboard.get_json()


def groups(direction: str) -> str:
    keyboard = Keyboard(inline=True)
    schedule = Schedule()

    filtered = [
        g for g in GROUPS if g.upper().startswith(direction.upper() + "-") or g.upper().startswith(direction.upper())
    ]

    for i, group in enumerate(filtered, start=1):
        keyboard.add(
            Callback(
                label=group,
                payload={"action": "group", "value": schedule.get_group_id(group)},
            )
        )
        if i % 2 == 0:
            keyboard.row()
    return keyboard.get_json()


def teachers(page: int = 0) -> str:
    keyboard = Keyboard(inline=True)
    schedule = Schedule()

    start = page * 8
    end = start + 8
    chunk = TEACHERS[start:end]

    for i, teacher in enumerate(chunk, start=1):
        keyboard.add(
            Callback(
                label=teacher,
                payload={
                    "action": "teacher",
                    "value": schedule.get_teacher_id(teacher),
                },
            )
        )

        if i % 2 == 0:
            keyboard.row()

    keyboard.row()

    if page > 0:
        keyboard.add(
            Callback(
                "⬅️ Назад",
                {"action": "teachers_page", "page": page - 1},
            )
        )

    if end < len(TEACHERS):
        keyboard.add(
            Callback(
                "Вперёд ➡️",
                {"action": "teachers_page", "page": page + 1},
            )
        )

    return keyboard.get_json()
