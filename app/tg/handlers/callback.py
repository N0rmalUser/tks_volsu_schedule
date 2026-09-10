import structlog
from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import get_schedule, get_today
from app.schemas.enums import Keyboard, Platform, WeekType
from app.services.schedule import ScheduleService
from app.services.user import UserService
from app.tg.filters import IgnoreFilter
from app.tg.markups import user as kb
from app.tg.markups.keyboard_factory import (
    ChangeCallbackFactory,
    DayCallbackFactory,
    DefaultChangeCallbackFactory,
)


router = Router()
log = structlog.get_logger()


@router.callback_query(DayCallbackFactory.filter(IgnoreFilter()))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action.in_(["day", "week"])))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподавателей,
    групп и аудиторий."""

    value: int = callback_data.value
    week: WeekType = callback_data.week
    day: int = callback_data.day
    keyboard: Keyboard = callback_data.keyboard
    log.info(
        "schedule.view",
        target=keyboard,
        target_id=value,
        week=week,
        day=day,
    )

    if callback_data.action == "week":
        week: WeekType = WeekType.ODD if callback_data.week != WeekType.EVEN else WeekType.EVEN

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(keyboard=keyboard, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    value: int = callback_data.value
    day, week = get_today()
    keyboard = Keyboard.ROOM

    log.info(
        "schedule.target_selected",
        target=callback_data.action,
        day=day,
        week=week,
        value=value,
    )

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(keyboard=keyboard, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action.in_(["group", "teacher"])))
async def group_teacher_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory, session: AsyncSession
) -> None:
    """Функция, обрабатывающая нажатие кнопок группы и преподавателя. Отправляет расписание на этот день для группы или
    преподавателя. Если преподаватель является учеником (указывается в core.toml), отправляет расписание его групп,
    смешанное с занятиями, которые он сам проводит"""

    value: int = callback_data.value
    day, week = get_today()
    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)

    if callback_data.action == "teacher":
        await service.set_teacher(value)
        keyboard = Keyboard.TEACHER
    else:
        await service.set_group(value)
        keyboard = Keyboard.STUDENT

    log.info(
        "schedule.target_selected",
        target=callback_data.action,
        day=day,
        week=week,
        value=value,
    )
    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(
            keyboard=keyboard,
            week=week,
            day=day,
            value=value,
        ),
    )
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_teacher"))
async def default_teacher_handler(
    callback: CallbackQuery, callback_data: DefaultChangeCallbackFactory, session: AsyncSession
) -> None:
    value: int = callback_data.value
    log.info(
        "settings.default_changed",
        target="teacher",
        target_id=value,
    )
    if value is None:
        await callback.message.edit_text("Выбор по умолчанию удалён")
        await callback.answer()
        return

    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)
    await service.set_default_id(value)
    await callback.message.edit_text(
        f"Преподаватель по умолчанию изменён на {await ScheduleService().get_teacher_name(value)}",
    )
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_group"))
async def default_group_handler(
    callback: CallbackQuery, callback_data: DefaultChangeCallbackFactory, session: AsyncSession
) -> None:
    value: int = callback_data.value
    log.info(
        "settings.default_changed",
        target="group",
        target_id=value,
    )
    if value is None:
        await callback.message.edit_text("Выбор по умолчанию удалён")
        await callback.answer()
        return

    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)

    await service.set_default_id(value)
    await callback.message.edit_text(
        f"Группа по умолчанию изменена на {await ScheduleService().get_group_name(value)}",
    )
    await callback.answer()
