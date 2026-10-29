import asyncio
import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.common.schedule_update import update_college_schedule


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TIMEZONE = ZoneInfo("Europe/Moscow")


async def scheduled_update() -> None:
    try:
        await update_college_schedule()
    except Exception:
        log.exception("schedule.automatic_update_failed")


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    scheduler.add_job(
        scheduled_update,
        trigger="cron",
        hour="7,12,18",
        minute=0,
        id="college_schedule_update",
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
    log.info("College schedule worker started")

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)
