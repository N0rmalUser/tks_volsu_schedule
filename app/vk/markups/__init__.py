from vkbottle import Keyboard, Callback, Text, KeyboardButtonColor

from app.config import TEACHERS, ROOMS, GROUPS
from app.database.schedule import Schedule


def menu() -> str:
    keyboard = Keyboard(one_time=True, inline=False)
    keyboard.add(
        Text("Расписание на сегодня"), color=KeyboardButtonColor.POSITIVE
    )
    keyboard.row()
    keyboard.add(
        Text("Группы")
    )
    keyboard.add(
        Text("Преподаватели")
    )
    keyboard.add(
        Text("Кабинеты")
    )
    return keyboard.get_json()


def days(keyboard_type: str, week: int, day: int, value: int) -> str:
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
        keyboard.add(
            Callback("Неизвестная неделя", {"action": "ignore"})
        )

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

def groups() -> str:
    keyboard = Keyboard(inline=True)
    schedule = Schedule()

    for i, group in enumerate(GROUPS, start=1):
        keyboard.add(
            Callback(
                label=str(group),
                payload={
                    "action": "group",
                    "value": schedule.get_room_id(group),
                },
            )
        )

        if i % 4 == 0:
            keyboard.row()

    return keyboard.get_json()

from vkbottle import Keyboard, Callback

PER_PAGE = 8  # 6 строк по 2 кнопки


def teachers(page: int = 0) -> str:
    keyboard = Keyboard(inline=True)

    schedule = Schedule()
    start = page * PER_PAGE
    end = start + PER_PAGE
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

    # --- навигация ---
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
