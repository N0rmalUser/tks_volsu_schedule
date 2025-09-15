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
from datetime import datetime

import app
from app.config import EVENT_LEVEL, LOG_FILE, LOG_LEVEL, TZ

if __name__ == "__main__":
    logging.Formatter.converter = lambda *args: datetime.now(TZ).timetuple()
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
            logging.StreamHandler(),
        ],
        force=True,
    )
    logging.getLogger("aiogram.event").setLevel(levels[EVENT_LEVEL])
    asyncio.run(app.main())
