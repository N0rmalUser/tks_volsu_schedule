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

from app.vk.markups import teachers

router = BotLabeler()

@router.raw_event("message_event", dataclass=MessageEvent)
async def teachers_page(event: MessageEvent):
    print(type(event))
    print(event.payload.get("action"))
    if event.payload.get("action") == "teachers_page":
        page = event.payload["page"]
        await event.ctx_api.messages.edit(
            peer_id=event.object.peer_id,
            conversation_message_id=event.object.conversation_message_id,
            keyboard=teachers(page),
            message="Выберите преподавателя",
        )
