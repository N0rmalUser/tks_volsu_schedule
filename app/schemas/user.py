from dataclasses import dataclass
from datetime import datetime

from app.schemas.enums import UserRole


@dataclass(frozen=True, slots=True)
class UserInfo:
    role: UserRole
    registered: datetime
    group_name: str | None
    teacher_name: str | None
    tracking: bool
    blocked: bool
