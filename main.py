import asyncio
from bot import bot, database as db
from config import LOG_FILE, timezone
from datetime import datetime
import logging
import pytz


def timetz(*args):
    return datetime.now(pytz.timezone(timezone)).timetuple()


if __name__ == "__main__":
    tz = pytz.timezone('Europe/Moscow')
    logging.Formatter.converter = timetz
    logging.basicConfig(level=logging.INFO, filename=LOG_FILE, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    db.init_db()
    asyncio.run(bot.main())
