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

from vkbottle.bot import BotLabeler, MessageEvent

from app.common.utils import get_schedule, get_today
from app.database.session import session_scope
from app.schemas.enums import Keyboard, Platform, WeekType
from app.services.user import UserService
from app.vk.markups import days, groups, teachers


router = BotLabeler()


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "teachers_page"},
)
async def teachers_page(event: MessageEvent) -> None:
    page = event.payload["page"]

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=teachers(page),
        message="Выберите преподавателя",
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "select_direction"},
)
async def select_direction_handler(event: MessageEvent) -> None:
    direction = event.payload["direction"]

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=groups(direction),
        message=f"Выберите группу {direction}",
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "teacher"},
)
async def teacher_handler(event: MessageEvent) -> None:
    day, week = get_today()
    value = event.payload.get("value")

    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, event.peer_id)

        await service.set_teacher(value)
        keyboard = Keyboard.TEACHER

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard, day, week, value),
        message=text,
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "group"},
)
async def group_handler(event: MessageEvent) -> None:
    day, week = get_today()
    value = event.payload.get("value")

    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, event.peer_id)

        await service.set_group(value)
        keyboard = Keyboard.STUDENT

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard, day, week, value),
        message=text,
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "room"},
)
async def room_handler(event: MessageEvent) -> None:
    day, week = get_today()
    value = event.payload.get("value")
    keyboard = Keyboard.ROOM

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard, day, week, value),
        message=text,
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "week"},
)
async def week_handler(event: MessageEvent) -> None:
    week = WeekType.ODD if event.payload.get("week") != WeekType.EVEN else WeekType.EVEN
    day = event.payload.get("day")
    value = event.payload.get("value")
    keyboard: Keyboard = event.payload.get("keyboard_type")

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard, day, week, value),
        message=text,
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "day"},
)
async def day_handler(event: MessageEvent) -> None:
    value = event.payload.get("value")
    day = event.payload.get("day")
    week = event.payload.get("week")
    keyboard: Keyboard = event.payload.get("keyboard_type")

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard, day, week, value),
        message=text,
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "ignore"},
)
async def ignore_handler(event: MessageEvent) -> None:
    await event.show_snackbar("Сейчас эта неделя")
