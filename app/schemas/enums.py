from enum import IntEnum, StrEnum


class WeekType(StrEnum):
    EVERY = "every"
    ODD = "odd"
    EVEN = "even"


class ActivityType(StrEnum):
    START = "start"
    SCHEDULE_VIEW = "schedule_view"
    DAY_VIEW = "day_view"
    TODAY_VIEW = "today_view"

    DEFAULT_TEACHER_SELECTED = "default_teacher_selected"
    DEFAULT_GROUP_SELECTED = "default_group_selected"


class DayOfWeek(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


class UserRole(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Platform(StrEnum):
    TELEGRAM = "telegram"
    VK = "vk"


class GroupType(StrEnum):
    COLLEGE = "college"
    UNIVERSITY = "university"


class Keyboard(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ROOM = "room"


WEEK_MAP = {
    1: WeekType.ODD,
    2: WeekType.EVEN,
}
