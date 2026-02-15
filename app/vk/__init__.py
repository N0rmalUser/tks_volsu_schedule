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

from vkbottle import Bot

from app.common import set_logging
from app.config import VK_BOT_TOKEN
from app.vk.handlers import message, callback


def main() -> None:
    bot = Bot(token=VK_BOT_TOKEN)
    bot.labeler.load(message.router)
    bot.labeler.load(callback.router)

    bot.run_forever()


if __name__ == "__main__":
    set_logging("vkbottle")
    main()
