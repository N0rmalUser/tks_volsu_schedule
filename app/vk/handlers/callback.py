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

from app.common import get_today, text_maker
from app.common.text_maker import text_formatter
from app.database.schedule import Schedule
from app.database.vkuser import VK_USER
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
    user = VK_USER(event.peer_id)
    user.teacher = value

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days("teacher", day, week, value),
        message=text_maker.get_teacher_schedule(
            day=day,
            week=week,
            teacher_name=Schedule().get_teacher_name(value),
        ),
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "group"},
)
async def group_handler(event: MessageEvent) -> None:
    day, week = get_today()
    value = event.payload.get("value")
    user = VK_USER(event.peer_id)
    user.group = value

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days("group", day, week, value),
        message=text_maker.get_group_schedule(
            day=day,
            week=week,
            group_name=Schedule().get_group_name(value),
        ),
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "room"},
)
async def room_handler(event: MessageEvent) -> None:
    day, week = get_today()
    value = event.payload.get("value")

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days("room", day, week, value),
        message=text_maker.get_room_schedule(
            day=day,
            week=week,
            room_name=Schedule().get_room_name(value),
        ),
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "week"},
)
async def week_handler(event: MessageEvent) -> None:
    week = 1 if int(event.payload.get("week")) != 2 else 2
    day = event.payload.get("day")
    value = event.payload.get("value")
    keyboard_type = event.payload.get("keyboard_type")

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard_type, day, week, value),
        message=await text_formatter(
            keyboard_type=keyboard_type,
            day=day,
            week=week,
            value=value,
        ),
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "day"},
)
async def day_handler(event: MessageEvent) -> None:
    keyboard_type = event.payload.get("keyboard_type")
    value = event.payload.get("value")
    day = event.payload.get("day")
    week = event.payload.get("week")

    await event.ctx_api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=days(keyboard_type, day, week, value),
        message=await text_formatter(
            keyboard_type=keyboard_type,
            day=day,
            week=week,
            value=value,
        ),
    )


@router.raw_event(
    "message_event",
    dataclass=MessageEvent,
    payload_contains={"action": "ignore"},
)
async def ignore_handler(event: MessageEvent) -> None:
    await event.show_snackbar("Сейчас эта неделя")
