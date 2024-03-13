import asyncio
from bot import bot, database as db
import config
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename=config.LOG_FILE, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    db.init_db()
    asyncio.run(bot.main())
