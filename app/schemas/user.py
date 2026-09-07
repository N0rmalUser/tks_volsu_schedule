from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
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
