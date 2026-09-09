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

import logging

import structlog
from vk.middlewares import LoggingMessageMiddleware, LoggingRawEventMiddleware
from vkbottle import Bot

from app.core.config import config
from app.core.logging_config import setup_logging
from app.vk.handlers import callback, message


log = structlog.get_logger()

def main() -> None:
    setup_logging()

    vkbottle_logger = logging.getLogger("vkbottle")

    vkbottle_logger.handlers.clear()
    vkbottle_logger.propagate = True

    bot = Bot(token=config.vk_bot_token)
    bot.labeler.load(message.router)
    bot.labeler.load(callback.router)
    bot.labeler.message_view.register_middleware(LoggingMessageMiddleware)
    bot.labeler.raw_event_view.register_middleware(LoggingRawEventMiddleware)

    log.info("bot_started")
    bot.run()


if __name__ == "__main__":
    main()
