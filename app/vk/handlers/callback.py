import structlog
from vkbottle.bot import BotLabeler, MessageEvent

from app.common.utils import get_schedule, get_today
from app.core.enums import Keyboard, Platform, WeekType
from app.database.session import session_scope
from app.services.user import UserService
from app.vk.markups import days, groups, teachers


router = BotLabeler()
log = structlog.get_logger()


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

    log.info(
        "schedule.target_selected",
        target="teacher",
        day=day,
        week=week,
        value=value,
    )
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

    log.info(
        "schedule.target_selected",
        target="group",
        day=day,
        week=week,
        value=value,
    )
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

    log.info(
        "schedule.target_selected",
        target="room",
        day=day,
        week=week,
        value=value,
    )
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
    week: WeekType = WeekType.ODD if event.payload.get("week") != WeekType.EVEN else WeekType.EVEN
    day = event.payload.get("day")
    value = event.payload.get("value")
    keyboard: Keyboard = event.payload.get("keyboard_type")

    log.info(
        "schedule.view",
        target=keyboard,
        target_id=value,
        week=week,
        day=day,
    )
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

    log.info(
        "schedule.view",
        target=keyboard,
        target_id=value,
        week=week,
        day=day,
    )
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
