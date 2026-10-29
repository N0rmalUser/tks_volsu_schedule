import structlog
from common.api_schedule_parser import parse_api_schedule
from core.enums import GroupType
from schemas.keyboard import init_keyboard_data
from services.schedule import ScheduleService

from app.common.docx_schedule_parser import parse_university_schedule


log = structlog.getLogger()


async def update_college_schedule() -> None:
    college_rows = await parse_api_schedule()

    await ScheduleService().import_schedule(
        rows=college_rows,
        group_type=GroupType.COLLEGE,
    )

    await init_keyboard_data()

    log.info("schedule.college_updated")


async def update_university_schedule() -> None:
    university_rows = parse_university_schedule()

    await ScheduleService().import_schedule(
        rows=university_rows,
        group_type=GroupType.UNIVERSITY,
    )
    await init_keyboard_data()
    log.info("schedule.university_updated")
