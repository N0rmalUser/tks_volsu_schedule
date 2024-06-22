from aiogram import Router
from aiogram.filters.chat_member_updated import (KICKED, MEMBER,
                                                 ChatMemberUpdatedFilter)
from aiogram.types import ChatMemberUpdated

from bot.database.user import UserDatabase

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания блокировки бота пользователем."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(event.from_user.id)
    user.blocked = True
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"Пользователь @{event.from_user.username} заблокировал бота",
        message_thread_id=user.topic_id,
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания разблокировки бота пользователем."""

    from bot.bot import bot
    from config import ADMIN_CHAT_ID

    user = UserDatabase(event.from_user.id)
    user.blocked = False

    await bot.send_message(
        ADMIN_CHAT_ID,
        f"Пользователь @{event.from_user.username} разблокировал бота",
        message_thread_id=user.topic_id,
    )
