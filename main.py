import asyncio

from bot import bot, database as db

from config import LOG_FILE

import logging


if __name__ == "__main__":
    db.init_db()
    db.open_schedule_file()
    logging.basicConfig(level=logging.INFO, filename=LOG_FILE, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    asyncio.run(bot.main())