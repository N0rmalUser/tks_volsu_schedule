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

from multiprocessing import Process

from app.common import set_logging


def run_vk_bot() -> None:
    from app.vk import main as vk_main

    set_logging("vkbottle")
    vk_main()


def run_tg_bot() -> None:
    import asyncio

    from app.tg import main as tg_main

    set_logging("aiogram.event")
    asyncio.run(tg_main())


if __name__ == "__main__":
    vk_process = Process(target=run_vk_bot)
    tg_process = Process(target=run_tg_bot)

    vk_process.start()
    tg_process.start()

    vk_process.join()
    tg_process.join()
