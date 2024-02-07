import asyncio
from bot import bot, database as db
import config
import json
import logging


def extract_and_sort_group_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    group_names = [group["group"] for group in data["groups"]]
    sorted_group_names = sorted(group_names)

    return sorted_group_names


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename=config.LOG_FILE, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt='%H:%M:%S %d-%m-%Y', encoding="utf-8")
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    config.groups = extract_and_sort_group_names(config.SCHEDULE_PATH)
    db.init_db()
    db.open_schedule_file()
    asyncio.run(bot.main())
