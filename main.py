import asyncio
from multiprocessing import Process

from app.tg.bot import main as tg_main
from app.vk.bot import main as vk_main


def run_tg_bot() -> None:
    asyncio.run(tg_main())


if __name__ == "__main__":
    vk_process = Process(target=vk_main)
    tg_process = Process(target=run_tg_bot)

    vk_process.start()
    tg_process.start()

    vk_process.join()
    tg_process.join()
