from dataclasses import dataclass
from datetime import time

from pydantic import BaseModel

from app.schemas.enums import WeekType


@dataclass(frozen=True, slots=True)
class ScheduleRow:
    group: str
    subject: str
    teacher: str | None
    room: str | None
    day_of_week: int
    lesson_number: int
    week_type: WeekType
    subgroup: int | None


@dataclass(frozen=True, slots=True)
class LessonTime:
    number: int
    start: time
    end: time


class ScheduleEntry(BaseModel):
    lesson_number: int | None
    day_of_week: int
    week_type: WeekType

    subject: str | None
    teacher: str | None
    room: str | None
    group: str | None
    subgroup: int | None


class ScheduleResponse(BaseModel):
    group: str
    day_of_week: int
    week_type: WeekType
    entries: list[ScheduleEntry]


class TeacherEntry(BaseModel):
    id: int
    name: str
