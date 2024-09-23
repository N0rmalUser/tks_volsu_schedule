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

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.schedule import Schedule
from app.database.user import UserDatabase
from app.markups import edit_markups as kb
from app.markups import user_markups as def_kb
from app.markups.keyboard_factory import (DayCallbackFactory,
                                          ScheduleConstructorCallbackFactory,
                                          ScheduleEditingCallbackFactory)
from app.misc import text_maker

router = Router()


async def func(callback: CallbackQuery, entity_id: int, kb_type: str):
    user = UserDatabase(callback.from_user.id)
    schedule_ids = []
    text = "Ошибка. Сообщите администратору /admin"
    if kb_type == "teacher":
        text = text_maker.get_teacher_schedule(
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
    import re

    from app.misc.text_maker import get_lesson_label, get_time_symbol

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
    Schedule().edit_day(schedule_id=callback_data.schedule_id, day=days[callback_data.day - 1])
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
        week=("Числитель" if UserDatabase(callback.from_user.id).week == 2 else "Знаменатель"),
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
    await callback.message.edit_reply_markup(
        reply_markup=kb.edit_teacher(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        )
    )
    await callback.answer()


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "teacher_edit"))
async def week_edit_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    Schedule().edit_teacher(
        schedule_id=callback_data.schedule_id,
        teacher=callback_data.edit,
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
    Schedule().edit_group(schedule_id=callback_data.schedule_id, group=callback_data.edit)
    await func(callback, callback_data.value, callback_data.keyboard_type)


@router.callback_query(ScheduleEditingCallbackFactory.filter(F.action == "room"))
async def room_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=kb.edit_room(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        )
    )
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
    await callback.message.edit_text(
        "Сначала выберите время, когда будет проводится занятие",
        reply_markup=kb.add_time(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_day"))
async def add_new_day_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    await callback.message.edit_text(
        "Теперь день",
        reply_markup=kb.add_day(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_week"))
async def add_new_week_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
) -> None:
    await callback.message.edit_text(
        "Теперь выберите неделю",
        reply_markup=kb.add_week(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_type"))
async def add_new_lesson_type_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    await callback.message.edit_text(
        "Теперь выберите тип занятия",
        reply_markup=kb.add_lesson_type(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )
    await callback.answer()


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_lesson"))
async def add_new_lesson_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
    state: FSMContext,
) -> None:
    from app.misc.states import NewSchedule

    await callback.message.edit_text(
        "Теперь напишите название дисциплины",
        reply_markup=kb.add_lesson(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )
    await state.update_data(callback=callback, callback_data=callback_data)
    await state.set_state(NewSchedule.lesson)
    print(state)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_group"))
async def add_new_group_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
    state: FSMContext,
) -> None:
    from app.misc.states import NewSchedule

    await state.clear()
    await callback.message.edit_text(
        "Теперь выберите группу или напишите её название (Например: РСК-211_2)",
        reply_markup=kb.add_group(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )
    await state.update_data(callback=callback, callback_data=callback_data)
    await state.set_state(NewSchedule.group)
    print(state)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_teacher"))
async def add_new_teacher_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
    state: FSMContext,
) -> None:
    from app.misc.states import NewSchedule

    await state.clear()
    await callback.message.edit_text(
        "Теперь выберите преподавателя или напишите его ФИО (Например: Иванов И.И.)",
        reply_markup=kb.add_teacher(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )
    await state.update_data(callback=callback, callback_data=callback_data)
    await state.set_state(NewSchedule.teacher)
    print(state)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_room"))
async def add_new_room_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
    state: FSMContext,
) -> None:
    from app.misc.states import NewSchedule

    await callback.message.edit_text(
        "Теперь выберите аудиторию или напишите ее номер слитно с корпусом (Например: 1-19М)",
        reply_markup=kb.add_room(
            schedule_id=callback_data.schedule_id,
            value=callback_data.value,
            keyboard_type=callback_data.keyboard_type,
        ),
    )
    await state.update_data(callback=callback, callback_data=callback_data)
    await state.set_state(NewSchedule.room)
    print(state)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "add_new_end"))
async def add_new_end_handler(
    callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory
) -> None:
    if callback_data.keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            teacher_name=Schedule().get_teacher_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            callback.from_user.id,
            "teacher",
            UserDatabase(callback.from_user.id).week,
            callback_data.value,
        )
    elif callback_data.keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            group_name=Schedule().get_group_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            callback.from_user.id,
            "group",
            UserDatabase(callback.from_user.id).week,
            callback_data.value,
        )
    elif callback_data.keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            room_name=Schedule().get_room_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            callback.from_user.id,
            "room",
            UserDatabase(callback.from_user.id).week,
            callback_data.value,
        )
    else:
        text = "Ошибка. Сообщите администратору /admin"
        keyboard = None
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "back"))
async def back_handler(
    callback: CallbackQuery,
    callback_data: ScheduleEditingCallbackFactory,
    state: FSMContext,
):
    if callback_data.previous == "add_new":
        await add_new_handler(callback, callback_data)
    elif callback_data.previous == "add_new_day":
        await add_new_day_handler(callback, callback_data)
    elif callback_data.previous == "add_new_week":
        await add_new_week_handler(callback, callback_data)
    elif callback_data.previous == "add_new_type":
        await state.clear()
        await add_new_lesson_type_handler(callback, callback_data)
    elif callback_data.previous == "add_new_lesson":
        await state.clear()
        await add_new_lesson_handler(callback, callback_data, state)
    elif callback_data.previous == "add_new_group":
        await state.clear()
        await add_new_group_handler(callback, callback_data, state)
    elif callback_data.previous == "add_new_teacher":
        await state.clear()
        await add_new_teacher_handler(callback, callback_data, state)
    elif callback_data.previous == "add_new_room":
        await state.clear()
        await add_new_room_handler(callback, callback_data, state)
    else:
        await callback.answer("Ошибка. Сообщите администратору /admin")


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "cancel"))
async def cancel_handler(callback: CallbackQuery, callback_data: ScheduleEditingCallbackFactory):
    if callback_data.keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            teacher_name=Schedule().get_teacher_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            user_id=callback.from_user.id,
            keyboard_type="teacher",
            week=UserDatabase(callback.from_user.id).week,
            value=callback_data.value,
        )
    elif callback_data.keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            group_name=Schedule().get_group_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            user_id=callback.from_user.id,
            keyboard_type="group",
            week=UserDatabase(callback.from_user.id).week,
            value=callback_data.value,
        )
    elif callback_data.keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=UserDatabase(callback.from_user.id).day,
            week=UserDatabase(callback.from_user.id).week,
            room_name=Schedule().get_room_name(callback_data.value),
        )
        keyboard = def_kb.get_days_teacher(
            user_id=callback.from_user.id,
            keyboard_type="room",
            week=UserDatabase(callback.from_user.id).week,
            value=callback_data.value,
        )
    else:
        text = "Ошибка. Сообщите администратору /admin"
        keyboard = None
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(ScheduleConstructorCallbackFactory.filter(F.action == "delete"))
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
        week_kb = def_kb.get_days_teacher(
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
        week_kb = def_kb.get_days_teacher(
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
        week_kb = def_kb.get_days_teacher(
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
