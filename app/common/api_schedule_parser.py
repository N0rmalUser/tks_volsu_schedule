import asyncio
from datetime import datetime, timedelta
from typing import Any

import structlog
from aiohttp import ClientError, ClientSession, ClientTimeout

from app.core.config import config
from app.core.constants import LESSON_LABELS_NAMES, TZ, WEEK_TYPE_MAP
from app.core.enums import WeekType
from app.schemas.schedule import ScheduleRow


log = structlog.get_logger()

def _get_dates() -> tuple[str, str]:
    now = datetime.now(TZ)
    start_dt = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        tzinfo=TZ,
    ) - timedelta(days=now.weekday())

    end_dt = start_dt + timedelta(days=13)

    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

    return start_date, end_date


def _map_class_type(raw_type: str) -> str:
    """Преобразует английский тип занятия в русский."""

    mapped = LESSON_LABELS_NAMES.get(raw_type.lower())
    if not mapped:
        raise ValueError(f"Неизвестный тип занятия: {raw_type}")
    return mapped


def _map_week_type(raw_type: str) -> WeekType:
    """Преобразует английский тип недели в enum WeekType."""

    mapped = WEEK_TYPE_MAP.get(raw_type.lower())
    if not mapped:
        raise ValueError(f"Неизвестный тип недели: {raw_type}")
    return mapped


def _extract_schedule_rows(teacher_data: dict[str, Any]) -> list[ScheduleRow]:
    """Парсит ответ API для одного преподавателя в список строк расписания."""

    rows: list[ScheduleRow] = []

    teachers = teacher_data.get("teachers", [])
    teacher_name = teachers[0]["name"] if teachers else "Неизвестный преподаватель"

    for day_data in teacher_data.get("days", []):
        day_of_week = day_data["dayOfWeek"]

        for lesson_entry in day_data.get("entries", []):
            rooms = lesson_entry.get("rooms", [])
            groups = lesson_entry.get("groupNames", [])

            subject_name = lesson_entry.get("subjectName", "Без названия")
            class_type_ru = _map_class_type(lesson_entry["classType"])
            subject = f"{subject_name} {class_type_ru}"

            rows.append(
                ScheduleRow(
                    group=groups[0],
                    subject=subject,
                    teacher=teacher_name,
                    room=rooms[0] if rooms else None,
                    day_of_week=day_of_week,
                    lesson_number=lesson_entry["slotNumber"],
                    week_type=_map_week_type(lesson_entry["weekType"]),
                    subgroup=lesson_entry.get("subgroup"),
                )
            )

    return rows


async def _fetch_teacher_schedule(session: ClientSession, params: dict[str, str]) -> dict | None:
    """Выполняет HTTP запрос к API для получения расписания преподавателя."""

    headers = {"X-API-Key": config.api_key}
    teacher_last_name = params.get("lastName", "Unknown")

    try:
        async with session.get(
            config.api_url,
            headers=headers,
            params=params,
            timeout=ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
            return await response.json()

    except ClientError:
        log.exception("Ошибка HTTP запроса", teacher=teacher_last_name)
        return None

    except TimeoutError:
        log.exception("Превышено время ожидания запроса", teacher=teacher_last_name)
        return None


async def parse_api_schedule() -> list[ScheduleRow]:
    """Собирает и парсит расписание всех преподавателей за указанный период."""

    all_schedule_rows: list[ScheduleRow] = []
    from_date, to_date = _get_dates()

    async with ClientSession() as session:
        tasks = []
        for teacher_full_name in config.college_teachers:
            parts = teacher_full_name.replace(".", " ").split()
            last_name = parts[0] if len(parts) > 0 else ""
            first_name = parts[1] if len(parts) > 1 else ""
            middle_name = parts[2] if len(parts) > 2 else ""

            params = {
                "lastName": last_name,
                "firstName": first_name,
                "middleName": middle_name,
                "from": from_date,
                "to": to_date,
            }
            tasks.append(_fetch_teacher_schedule(session, params))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    for teacher_name, result in zip(config.college_teachers, results, strict=False):
        if isinstance(result, Exception):
            log.error("Непредвиденное исключение при обработке", teacher=teacher_name, error=str(result))
            continue

        if result is None:
            log.error("Не удалось получить расписание", teacher=teacher_name)
            continue

        teacher_rows = _extract_schedule_rows(result)
        all_schedule_rows.extend(teacher_rows)

    log.info("Сбор расписания завершен", total_teachers=len(config.college_teachers), total_rows=len(all_schedule_rows))
    return all_schedule_rows
