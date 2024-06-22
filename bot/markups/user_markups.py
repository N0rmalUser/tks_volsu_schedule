from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from bot.database.user import UserDatabase
from bot.markups import keyboard_factory

student_menu = [
    [KeyboardButton(text="Расписание на сегодня")],
    [KeyboardButton(text="Группы"), KeyboardButton(text="Преподаватели")],
]
teacher_menu = [
    [KeyboardButton(text="Расписание на сегодня")],
    [
        KeyboardButton(text="Группы"),
        KeyboardButton(text="Преподаватели"),
        KeyboardButton(text="Кабинеты"),
    ],
]


student_menu = ReplyKeyboardMarkup(keyboard=student_menu, resize_keyboard=True)
teacher_menu = ReplyKeyboardMarkup(keyboard=teacher_menu, resize_keyboard=True)


def get_teachers():
    """Возвращает клавиатуру с преподавателями, указанными в config.py."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for teacher in config.teachers:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="teacher", value=Schedule().get_teacher_id(teacher)
            ),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_groups():
    """Возвращает клавиатуру с группами, указанными в config.py."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for group in config.groups:
        builder.button(
            text=group,
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="group", value=Schedule().get_group_id(group)
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_rooms():
    """Возвращает клавиатуру с аудиториями, указанными в config.py."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="room", value=Schedule().get_room_id(room)
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_default_teachers():
    """Возвращает клавиатуру с преподавателями, указанными в config.py."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for teacher in config.all_teachers:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_teacher", value=Schedule().get_teacher_id(teacher)
            ),
        )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(
            action="default_teacher", value=None
        ),
    )
    builder.adjust(2)
    return builder.as_markup()


def get_default_groups():
    """Возвращает клавиатуру с группами, указанными в config.py."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for group in config.groups:
        builder.button(
            text=group,
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_group", value=Schedule().get_group_id(group)
            ),
        )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(
            action="default_group", value=None
        ),
    )
    builder.adjust(3)
    return builder.as_markup()


def get_days(user_id: int, keyboard_type: str, week: int, value: int):
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}[day]
        builder.button(
            text=day,
            callback_data=keyboard_factory.DayCallbackFactory(
                action="day",
                keyboard_type=keyboard_type,
                day=int_day,
                week=week,
                value=value,
            ),
        )
    if week == 1:
        builder.button(
            text="✅ Числитель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="Знаменатель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=2,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    elif week == 2:
        builder.button(
            text="✅ Знаменатель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="Числитель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=1,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    else:
        builder.button(
            text="Неизвестная неделя",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_days_teacher(user_id: int, keyboard_type: str, week: int, value: int):
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    from bot.database.user import UserDatabase

    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}[day]
        builder.button(
            text=str(day),
            callback_data=keyboard_factory.DayCallbackFactory(
                action="day",
                keyboard_type=keyboard_type,
                day=int_day,
                week=week,
                value=value,
            ),
        )
    if week == 1:
        builder.button(
            text="✅ Числитель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="✏ Изменить ",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="schedule_editing", day=UserDatabase(user_id).day, value=value
            ),
        )
        builder.button(
            text="Знаменатель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=2,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    elif week == 2:
        builder.button(
            text="✅ Знаменатель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="✏ Изменить ",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="schedule_editing", day=UserDatabase(user_id).day, value=value
            ),
        )
        builder.button(
            text="Числитель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=1,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    else:
        builder.button(
            text="Неизвестная неделя",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_editing_menu(schedule_id: int, week: int, value: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Время",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="День",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Неделя",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="week_edit",
            edit="2" if week == 1 else "1",
            schedule_id=schedule_id,
            value=value,
        ),
    )
    builder.button(
        text="Тип занятия",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="lesson_type", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Преподаватель",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="teacher", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Группа",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="group", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Аудитория",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="room", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Удалить",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="delete", value=value, schedule_id=schedule_id
        ),
    )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(3)
    return builder.as_markup()


def get_editing(user_id: int, schedule: list, value: int):
    builder = InlineKeyboardBuilder()
    day = UserDatabase(user_id).day
    for i in schedule:
        builder.button(
            text=str(i),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="lesson", schedule_id=i, value=value
            ),
        )
    builder.adjust(2)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.extend([1, 1])
    builder.button(
        text="Добавить",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="add_new", day=day, value=value
        ),
    )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="cancel", day=day, value=value
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def add_new_lesson(user_id: int, value: int):
    day = UserDatabase(user_id).day
    builder = InlineKeyboardBuilder()
    builder.button(
        text="тоже отмена",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="cancel", day=day, value=value
        ),
    )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="cancel", day=day, value=value
        ),
    )


def edit_time(schedule_id: int, value: int):

    builder = InlineKeyboardBuilder()
    builder.button(
        text="08:30",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="0", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="10:10",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="1", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="12:00",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="2", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="13:40",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="3", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="15:20",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="4", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="17:00",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="5", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="18:40",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="time_edit", edit="6", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(4)
    return builder.as_markup()


def edit_day(schedule_id: int, value: int):

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Пн",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=1, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Вт",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=2, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Ср",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=3, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Чт",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=4, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Пт",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=5, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Сб",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="day_edit", day=6, schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(3)
    return builder.as_markup()


def edit_week(schedule_id: int, week: int, value: int):
    builder = InlineKeyboardBuilder()
    if week == 1:
        builder.button(
            text="Знаменатель",
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="week_edit", edit="2", schedule_id=schedule_id, value=value
            ),
        )
    else:
        builder.button(
            text="Числитель",
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="week_edit", edit="1", schedule_id=schedule_id, value=value
            ),
        )
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", edit="1", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(1)
    return builder.as_markup()


def edit_lesson_type(schedule_id: int, value: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Лекция",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit", edit="л", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Практика",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit", edit="пр", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Лабораторная",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit", edit="лаб", schedule_id=schedule_id, value=value
        ),
    )
    builder.button(
        text="Курсовой проект",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="type_edit", edit="курс", schedule_id=schedule_id, value=value
        ),
    )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_teacher(schedule_id: int, value: int):

    builder = InlineKeyboardBuilder()

    for teacher in config.teachers:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="teacher_edit",
                edit=teacher,
                value=value,
                schedule_id=schedule_id,
            ),
        )

    builder.adjust(2)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_group(schedule_id: int, value: int):
    builder = InlineKeyboardBuilder()
    for group in config.groups:
        builder.button(
            text=group,
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="group_edit", edit=group, value=value, schedule_id=schedule_id
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()


def edit_room(schedule_id: int, value: int):
    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
                action="room_edit", edit=room, value=value, schedule_id=schedule_id
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="Назад",
        callback_data=keyboard_factory.ScheduleEditingCallbackFactory(
            action="back", value=value, schedule_id=schedule_id
        ),
    )
    builder.adjust(*rows)
    return builder.as_markup()
