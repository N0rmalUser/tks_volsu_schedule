import structlog
from aiogram import Router
from aiogram.filters.chat_member_updated import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.enums import Platform
from app.services.user import UserService


router = Router()
log = structlog.get_logger()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """Хендлер для считывания блокировки бота пользователем."""

    log.info("block_bot")
    service = await UserService.create(session, Platform.TELEGRAM, event.from_user.id)
    await service.set_bot_blocked(True)
    topic_id = await service.get_tg_topic_id()

    await event.bot.send_message(
        config.admin_chat_id,
        message_thread_id=topic_id,
        text=f"Пользователь @{event.from_user.username} заблокировал бота",
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """Хендлер для считывания разблокировки бота пользователем."""

    service = await UserService.create(session, Platform.TELEGRAM, event.from_user.id)

    await service.set_bot_blocked(False)
    topic_id = await service.get_tg_topic_id()

    await event.bot.send_message(
        config.admin_chat_id,
        message_thread_id=topic_id,
        text=f"Пользователь @{event.from_user.username} разблокировал бота",
    )
