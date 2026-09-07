import asyncio
from multiprocessing import Process

from app.core.logger import set_logging
from app.tg.bot import main as tg_main
from app.vk.bot import main as vk_main


def run_vk_bot() -> None:

    set_logging("vkbottle")
    vk_main()


def run_tg_bot() -> None:

    set_logging("aiogram.event")
    asyncio.run(tg_main())


if __name__ == "__main__":
    vk_process = Process(target=run_vk_bot)
    vk_process.start()
    vk_process.join()

    tg_process = Process(target=run_tg_bot)
    tg_process.start()
    tg_process.join()
