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

import asyncio
import logging
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from bot import bot
from bot.config import EVENT_LEVEL, LOG_LEVEL, TIMEZONE
from bot.database.db_init import db_init


def start_scheduler():
    """Запускает планировщик задач, который обновляет статистику активности пользователей каждый час."""

    from bot.database.activity import update_user_activity_stats

    scheduler = BackgroundScheduler()
    next_hour = (datetime.now(pytz.timezone(TIMEZONE)) + timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    scheduler.add_job(update_user_activity_stats, "interval", hours=1, start_date=next_hour)
    scheduler.start()


if __name__ == "__main__":
    logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone(TIMEZONE)).timetuple()
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARN,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "EXCEPTION": logging.ERROR,
    }
    logging.basicConfig(
        level=levels[LOG_LEVEL],
        # filename=LOG_FILE,
        format="%(asctime)s %(levelname)s  %(message)s",
        datefmt="%H:%M:%S %d-%m-%Y",
        encoding="utf-8",
    )
    logging.getLogger("aiogram.event").setLevel(levels[EVENT_LEVEL])
    db_init()
    start_scheduler()
    asyncio.run(bot.main())
