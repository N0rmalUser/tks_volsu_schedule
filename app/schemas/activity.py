from datetime import date, datetime

from pydantic import BaseModel


class ActivityDayStat(BaseModel):
    date: date
    user_count: int


class ActivityHourStat(BaseModel):
    hour: datetime
    user_count: int
