import asyncio
from bot import bot, database as db
import config
import logging
import sqlite3


# def extract_and_sort_group_names(file_path):
#     conn = sqlite3.connect(config.SCHEDULE_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT DISTINCT GroupName
#         FROM Groups
#         GROUP BY GroupName
#         """)
#     group_names = cursor.fetchall()
#     groups = [row[0] for row in group_names]
#
#     return sorted(groups)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename=config.LOG_FILE, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    # config.groups = extract_and_sort_group_names(config.SCHEDULE_PATH)
    db.init_db()
    asyncio.run(bot.main())
