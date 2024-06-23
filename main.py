from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from bot import bot
from bot.database.db_init import db_init
from config import LOG_FILE, timezone
from datetime import datetime, timedelta
import logging
import pytz


def start_scheduler():
    """Запускает планировщик задач, который обновляет статистику активности пользователей каждый час."""

    from bot.database.activity import update_user_activity_stats

    scheduler = BackgroundScheduler()
    next_hour = (datetime.now(pytz.timezone(timezone)) + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    scheduler.add_job(update_user_activity_stats, 'interval', hours=1, start_date=next_hour)
    scheduler.start()


if __name__ == "__main__":
    logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone(timezone)).timetuple()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s  %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    db_init()
    start_scheduler()
    asyncio.run(bot.main())
