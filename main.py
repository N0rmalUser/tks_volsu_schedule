from multiprocessing import Process

from app.core.logger import set_logging


def run_vk_bot() -> None:
    from app.vk.bot import main as vk_main

    set_logging("vkbottle")
    vk_main()


def run_tg_bot() -> None:
    import asyncio

    from app.tg.bot import main as tg_main

    set_logging("aiogram.event")
    asyncio.run(tg_main())


if __name__ == "__main__":
    vk_process = Process(target=run_vk_bot)
    tg_process = Process(target=run_tg_bot)

    vk_process.start()
    tg_process.start()

    vk_process.join()
    tg_process.join()
