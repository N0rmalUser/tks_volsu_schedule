import logging

import structlog
from vkbottle import Bot

from app.core.config import config
from app.core.logging_config import setup_logging
from app.vk.handlers import callback, message
from app.vk.middlewares import LoggingMessageMiddleware, LoggingRawEventMiddleware


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
