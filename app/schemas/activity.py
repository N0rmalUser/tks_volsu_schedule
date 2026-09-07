from typing import TYPE_CHECKING

from pydantic import BaseModel


if TYPE_CHECKING:
    from datetime import date, datetime


class ActivityDayStat(BaseModel):
    date: date
    user_count: int


class ActivityHourStat(BaseModel):
    hour: datetime
    user_count: int
