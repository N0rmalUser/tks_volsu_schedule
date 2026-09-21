from app.core.config import config
from app.services.schedule import ScheduleService


class KeyboardData:
    teacher_ids: dict[str, int]
    group_ids: dict[str, int]
    room_ids: dict[str, int]


keyboard_data = KeyboardData()


async def init_keyboard_data() -> None:
    service = ScheduleService()

    sorted_groups = sorted([group for group in config.groups if group != "-"])

    keyboard_data.teacher_ids = await service.get_teacher_ids(config.all_personal)
    keyboard_data.group_ids = await service.get_group_ids(sorted_groups)
    keyboard_data.room_ids = await service.get_room_ids(config.rooms)
