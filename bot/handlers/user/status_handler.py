from aiogram import Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

from bot import database as db
from bot.filters import ChatTypeFilter

import importlib

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED), ChatTypeFilter(chat_type="private"))
async def user_blocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания блокировки бота пользователем."""
    db.set_blocked(event.from_user.id, True)
    await getattr(importlib.import_module("bot.bot"), "send_user_status")(event, "заблокировал")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER), ChatTypeFilter(chat_type="private"))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания разблокировки бота пользователем."""
    db.set_blocked(event.from_user.id, False)
    await getattr(importlib.import_module("bot.bot"), "send_user_status")(event, "разблокировал")
