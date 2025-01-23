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

import time
start_time = time.monotonic()

import asyncio
import logging

from datetime import datetime

import pytz

from app import bot
from app.config import EVENT_LEVEL, LOG_FILE, LOG_LEVEL, TIMEZONE

if __name__ == "__main__":
    logging.Formatter.converter = lambda *args: datetime.now(
        pytz.timezone(TIMEZONE)
    ).timetuple()
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
        format="%(asctime)s %(levelname)s  %(message)s",
        datefmt="%H:%M:%S %d-%m-%Y",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            # logging.StreamHandler()
        ]
    )
    logging.getLogger("aiogram.event").setLevel(levels[EVENT_LEVEL])
    logging.debug(f"Starting at {start_time}")
    logging.critical(f"Bot started in {(time.monotonic() - start_time):.2f} seconds.")
    asyncio.run(bot.main())
