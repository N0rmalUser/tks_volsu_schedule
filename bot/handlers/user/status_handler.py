from aiogram import Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

from bot.database.user import UserDatabase

import importlib

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания блокировки бота пользователем."""
    UserDatabase(event.from_user.id).blocked = True
    await getattr(importlib.import_module("bot.bot"), "send_user_status")(event, "заблокировал")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания разблокировки бота пользователем."""
    UserDatabase(event.from_user.id).blocked = False
    await getattr(importlib.import_module("bot.bot"), "send_user_status")(event, "разблокировал")
