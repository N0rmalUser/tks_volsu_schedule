import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.database.schedule import Schedule
from bot.database.user import UserDatabase
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import (ChangeCallbackFactory,
                                          DayCallbackFactory,
                                          DefaultChangeCallbackFactory,
                                          ScheduleEditingCallbackFactory)
from bot.misc import text_maker

router = Router()


@router.callback_query(DayCallbackFactory.filter(F.action == "ignore"))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action == "day"))
async def day_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподов, групп и аудиторий."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    keyboard_type: str = callback_data.keyboard_type
    value: int = callback_data.value
    week: int = callback_data.week
    day: int = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == user.day:
        await callback.answer()
        return
    user.day = callback_data.day

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=day, week=week, teacher_name=Schedule().get_teacher_name(value)
        )
        if user.type == "teacher":
            week_kb = kb.get_days_teacher(
                callback.from_user.id, keyboard_type="teacher", week=week, value=value
            )
        else:
            week_kb = kb.get_days(
                callback.from_user.id, keyboard_type="teacher", week=week, value=value
            )
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=day, week=week, group_name=Schedule().get_group_name(value)
        )
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type="group", week=week, value=value
        )
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=day, week=week, room_name=Schedule().get_room_name(value)
        )
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type="room", week=week, value=value
        )
    else:
        logging.error(
            f"{callback.from_user.id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler"
        )
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    """Функция, обрабатывающая нажатие кнопки недели. Отправляет расписание на следующую неделю для преподов, групп и аудиторий, сохраняя день."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    keyboard_type = callback_data.keyboard_type
    value: int = callback_data.value
    week = 1 if int(callback_data.week) != 2 else 2
    day = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == str(user.day):
        await callback.answer()
        return
    user.set_day = callback_data.day

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=day, week=week, teacher_name=Schedule().get_teacher_name(value)
        )
        if user.type == "teacher":
            week_kb = kb.get_days_teacher(
                callback.from_user.id, keyboard_type="teacher", week=week, value=value
            )
        else:
            week_kb = kb.get_days(
                callback.from_user.id, keyboard_type="teacher", week=week, value=value
            )
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=day, week=week, group_name=Schedule().get_group_name(value)
        )
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type="group", week=week, value=value
        )
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=day, week=week, room_name=Schedule().get_room_name(value)
        )
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type="room", week=week, value=value
        )
    else:
        logging.error(
            f"{callback.from_user.id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler"
        )
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()

    await callback.message.edit_text(
        text_maker.get_room_schedule(
            day=user.day,
            week=user.week,
            room_name=Schedule().get_room_name(callback_data.value),
        ),
        reply_markup=kb.get_days(
            callback.from_user.id,
            keyboard_type="room",
            week=user.week,
            value=callback_data.value,
        ),
    )
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(ChangeCallbackFactory.filter(F.action == "teacher"))
async def teacher_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    """Функция, обрабатывающая нажатие кнопки преподавателя. Отправляет расписание на этот день для преподавателя.
    Если преподаватель является учеником (указывается в config.py), отправляет расписание его групп, смешанное с занятиями, которые он сам проводит
    """

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.teacher = callback_data.value

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type="teacher",
            week=user.week,
            value=callback_data.value,
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id,
            keyboard_type="teacher",
            week=user.week,
            value=callback_data.value,
        )
    await callback.message.edit_text(
        text_maker.get_teacher_schedule(
            day=user.day,
            week=user.week,
            teacher_name=Schedule().get_teacher_name(callback_data.value),
        ),
        reply_markup=week_kb,
    )
    await callback.answer()
    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(ChangeCallbackFactory.filter(F.action == "group"))
async def group_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    """Функция, обрабатывающая нажатие кнопки группы. Отправляет расписание на этот день для группы."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.group = callback_data.value

    await callback.message.edit_text(
        text_maker.get_group_schedule(
            day=user.day,
            week=user.week,
            group_name=Schedule().get_group_name(callback_data.value),
        ),
        reply_markup=kb.get_days(
            callback.from_user.id,
            keyboard_type="group",
            week=user.week,
            value=callback_data.value,
        ),
    )
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(
    DefaultChangeCallbackFactory.filter(F.action == "default_teacher")
)
async def default_teacher_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value

    await callback.message.edit_text(f"Default изменён на {callback_data.value}")
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_group"))
async def default_group_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value

    await callback.message.edit_text(f"Default изменён на {callback_data.value}")
    await callback.answer()

    if user.tracking:
        await bot.send_message(
            ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data
        )


@router.callback_query(DayCallbackFactory.filter(F.action == "schedule_editing"))
async def schedule_editing_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    from bot.misc import text_maker_editing as tme

    teacher_id = callback_data.value

    user = UserDatabase(callback.from_user.id)
    text = tme.get_teacher_schedule(
        day=user.day,
        week=user.week,
        teacher_name=Schedule().get_teacher_name(callback_data.value),
    )

    schedule = Schedule().get_schedules_id(
        day=user.day,
        week=user.week,
        teacher_name=Schedule().get_teacher_name(callback_data.value),
    )
    if schedule is []:
        week_kb = kb.add_new_lesson(user_id=callback.from_user.id, value=teacher_id)
    else:
        week_kb = kb.get_editing(
            user_id=callback.from_user.id, value=teacher_id, schedule=schedule
        )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "lesson"))
async def lesson_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    from bot.misc.text_maker import get_time_symbol

    keyboard = kb.get_editing_menu(
        schedule_id=callback_data.schedule_id,
        week=UserDatabase(callback.from_user.id).week,
        value=callback_data.value,
    )
    time, day, week, subject, group, room, teacher = Schedule().get_schedule(
        schedule_id=callback_data.schedule_id
    )
    text = f"{day}       {week}\n{teacher}\n"

    import re

    from bot.misc.text_maker import get_lesson_label

    label = get_lesson_label(str(re.search(r"\(([^)]*)\)", subject)))
    subject = re.sub(r"\([^)]*\)", "", subject)
    text += f"\n👨🏻‍💻 {callback_data.schedule_id}\n{get_time_symbol(time)}{time}       {label}\n📖 {subject}\n👫 {group}\n🏠 {room}\n"

    await callback.message.edit_text(text=text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "time"))
async def time_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    keyboard = kb.edit_time(
        schedule_id=callback_data.schedule_id, value=callback_data.value
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "time_edit"))
async def time_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    times = ["8:30", "10:10", "12:00", "13:40", "15:20", "17:00", "18:40"]
    Schedule().edit_time(
        schedule_id=callback_data.schedule_id, time=times[int(callback_data.edit)]
    )
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "day"))
async def day_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    keyboard = kb.edit_day(
        schedule_id=callback_data.schedule_id, value=callback_data.value
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "day_edit"))
async def day_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    Schedule().edit_day(
        schedule_id=callback_data.schedule_id, day=days[callback_data.day - 1]
    )
    await schedule_editing_handler(callback, callback_data)


# @router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "week"))
# async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
#
#     keyboard = kb.edit_week(schedule_id=callback_data.schedule_id,
#                             week=UserDatabase(callback.from_user.id).week,
#                             value=callback_data.value)
#     await callback.message.edit_reply_markup(reply_markup=keyboard)
#     await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "week_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().edit_week(
        schedule_id=callback_data.schedule_id,
        week=(
            "Числитель"
            if UserDatabase(callback.from_user.id).week == 2
            else "Знаменатель"
        ),
    )
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "lesson_type"))
async def lesson_type_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    schedule_id = callback_data.schedule_id
    value = callback_data.value

    keyboard = kb.edit_lesson_type(schedule_id=schedule_id, value=value)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "type_edit"))
async def lesson_type_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().edit_lesson_type(
        schedule_id=callback_data.schedule_id, lesson_type=callback_data.edit
    )
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "teacher"))
async def teacher_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    keyboard = kb.edit_teacher(
        schedule_id=callback_data.schedule_id, value=callback_data.value
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(
    ScheduleEditingCallbackFactory.filter(F.action == "teacher_edit")
)
async def week_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().edit_teacher(
        schedule_id=callback_data.schedule_id,
        teacher=Schedule().get_teacher_id(callback_data.edit),
    )
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "group"))
async def group_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    keyboard = kb.edit_group(
        schedule_id=callback_data.schedule_id, value=callback_data.value
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "group_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().edit_group(
        schedule_id=callback_data.schedule_id, group=callback_data.edit
    )
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "room"))
async def room_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    keyboard = kb.edit_room(
        schedule_id=callback_data.schedule_id, value=callback_data.value
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "room_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().edit_room(schedule_id=callback_data.schedule_id, room=callback_data.edit)
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "add_new"))
async def add_new_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    pass


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "delete"))
async def delete_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    Schedule().delete_schedule(schedule_id=callback_data.schedule_id)
    await schedule_editing_handler(callback, callback_data)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "cancel"))
async def cancel_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    value = callback_data.value
    week = UserDatabase(callback.from_user.id).week

    text = text_maker.get_teacher_schedule(
        day=callback_data.day,
        week=week,
        teacher_name=Schedule().get_teacher_name(value),
    )
    week_kb = kb.get_days_teacher(
        callback.from_user.id, keyboard_type="teacher", week=week, value=value
    )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "back"))
async def back_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:
    await schedule_editing_handler(callback, callback_data)
