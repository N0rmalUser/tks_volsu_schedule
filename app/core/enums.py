from enum import IntEnum, StrEnum


class WeekType(StrEnum):
    EVERY = "every"
    ODD = "odd"
    EVEN = "even"


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
