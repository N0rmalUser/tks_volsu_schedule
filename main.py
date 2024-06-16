import asyncio
from bot import bot
from bot.database import activity as db, utils
from config import LOG_FILE, timezone
from datetime import datetime
import logging
import pytz


def timetz(*args):
    return datetime.now(pytz.timezone(timezone)).timetuple()


if __name__ == "__main__":
    logging.Formatter.converter = timetz
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    utils.initialize_db()
    db.init_db_activity()
    asyncio.run(bot.main())
