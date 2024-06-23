from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.database.schedule import Schedule
from bot.database.user import UserDatabase
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import (DayCallbackFactory,
                                          ScheduleEditingCallbackFactory)
from bot.misc import text_maker

router = Router()


async def func(callback: CallbackQuery, entity_id: int, kb_type: str):

    user = UserDatabase(callback.from_user.id)
    schedule_ids = []
    text = "Ошибка. Сообщите администратору /admin"
    if kb_type == "teacher":
        text = text_maker.get_teacher_schedule(
            # TODO: Переписать day и week через self внутри класса
            day=user.day,
            week=user.week,
            teacher_name=Schedule().get_teacher_name(entity_id),
            editing=True,
        )
        schedule_ids = Schedule().get_schedule_id_by_teacher(
            day=user.day,
            week=user.week,
            teacher_name=Schedule().get_teacher_name(entity_id),
        )
    elif kb_type == "group":
        text = text_maker.get_group_schedule(
            day=user.day,
            week=user.week,
            group_name=Schedule().get_group_name(entity_id),
            editing=True,
        )
        schedule_ids = Schedule().get_schedule_id_by_group(
            day=user.day,
            week=user.week,
            group_name=Schedule().get_group_name(entity_id),
        )
    elif kb_type == "room":
        text = text_maker.get_room_schedule(
            day=user.day,
            week=user.week,
            room_name=Schedule().get_room_name(entity_id),
            editing=True,
        )
        schedule_ids = Schedule().get_schedule_id_by_room(
            day=user.day,
            week=user.week,
            room_name=Schedule().get_room_name(entity_id),
        )

    if schedule_ids is []:
        week_kb = kb.add_new_lesson(
            user_id=callback.from_user.id, value=entity_id, keyboard_type=kb_type
        )
    else:
        week_kb = kb.get_editing(
            user_id=callback.from_user.id,
            value=entity_id,
            schedule_ids=schedule_ids,
            keyboard_type=kb_type,
        )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "schedule_editing"))
async def schedule_editing_handler(
    callback: CallbackQuery, callback_data: DayCallbackFactory
) -> None:

    await func(callback, callback_data.value, kb_type=callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "lesson"))
async def lesson_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    from bot.misc.text_maker import get_time_symbol

    keyboard = kb.get_editing_menu(
        schedule_id=callback_data.schedule_id,
        week=UserDatabase(callback.from_user.id).week,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    time, day, week, subject, group, room, teacher = Schedule().get_schedule(
        schedule_id=callback_data.schedule_id
    )
    text = f"{day}       {week}\n{teacher}\n\n"

    import re

    from bot.misc.text_maker import get_lesson_label

    label = get_lesson_label(str(re.search(r"\(([^)]*)\)", subject)))
    subject = re.sub(r"\([^)]*\)", "", subject)
    text += (
        f"👨🏻‍💻 {callback_data.schedule_id}\n"
        f"{get_time_symbol(time)}{time}       {label}\n"
        f"📖 {subject}\n"
        f"👫 {group}\n🏠"
        f" {room}\n"
    )

    await callback.message.edit_text(text=text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "time"))
async def time_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    keyboard = kb.edit_time(
        schedule_id=callback_data.schedule_id,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "time_edit"))
async def time_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    times = ["8:30", "10:10", "12:00", "13:40", "15:20", "17:00", "18:40"]
    Schedule().edit_time(
        schedule_id=callback_data.schedule_id, time=times[int(callback_data.edit)]
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "day"))
async def day_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    keyboard = kb.edit_day(
        schedule_id=callback_data.schedule_id,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "day_edit"))
async def day_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    Schedule().edit_day(
        schedule_id=callback_data.schedule_id, day=days[callback_data.day - 1]
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


# @router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "week"))
# async def week_handler(callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory) -> None:
#
#     keyboard = kb.edit_week(schedule_id=callback_data.schedule_id,
#                             week=UserDatabase(callback.from_user.id).week,
#                             value=callback_data.value)
#     await callback.message.edit_reply_markup(reply_markup=keyboard)
#     await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "week_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().edit_week(
        schedule_id=callback_data.schedule_id,
        week=(
            "Числитель"
            if UserDatabase(callback.from_user.id).week == 2
            else "Знаменатель"
        ),
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "lesson_type"))
async def lesson_type_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    schedule_id = callback_data.schedule_id
    value = callback_data.value

    keyboard = kb.edit_lesson_type(
        schedule_id=schedule_id, value=value, keyboard_type=callback_data.keyboard_type
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "type_edit"))
async def lesson_type_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().edit_lesson_type(
        schedule_id=callback_data.schedule_id, lesson_type=callback_data.edit
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "teacher"))
async def teacher_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    keyboard = kb.edit_teacher(
        schedule_id=callback_data.schedule_id,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(
    ScheduleEditingCallbackFactory.filter(F.action == "teacher_edit")
)
async def week_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().edit_teacher(
        schedule_id=callback_data.schedule_id,
        teacher=Schedule().get_teacher_id(callback_data.edit),
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "group"))
async def group_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    keyboard = kb.edit_group(
        schedule_id=callback_data.schedule_id,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "group_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().edit_group(
        schedule_id=callback_data.schedule_id, group=callback_data.edit
    )
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "room"))
async def room_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    keyboard = kb.edit_room(
        schedule_id=callback_data.schedule_id,
        value=callback_data.value,
        keyboard_type=callback_data.keyboard_type,
    )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "room_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().edit_room(schedule_id=callback_data.schedule_id, room=callback_data.edit)
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "add_new"))
async def add_new_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    pass


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "delete"))
async def delete_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:

    Schedule().delete_schedule(schedule_id=callback_data.schedule_id)
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "cancel"))
async def cancel_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    value = callback_data.value
    week = UserDatabase(callback.from_user.id).week

    text = "Ошибка. Сообщите администратору /admin"
    week_kb = None
    if callback_data.keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=callback_data.day,
            week=week,
            teacher_name=Schedule().get_teacher_name(value),
        )
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type=callback_data.keyboard_type,
            week=week,
            value=value,
        )
    elif callback_data.keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=callback_data.day,
            week=week,
            group_name=Schedule().get_group_name(value),
        )
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type=callback_data.keyboard_type,
            week=week,
            value=value,
        )
    elif callback_data.keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=callback_data.day,
            week=week,
            room_name=Schedule().get_room_name(value),
        )
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type=callback_data.keyboard_type,
            week=week,
            value=value,
        )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "back"))
async def back_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    await func(callback, callback_data.value, callback_data.keyboard_type)
