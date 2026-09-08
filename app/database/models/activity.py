from datetime import datetime

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.schemas.enums import ActivityType


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    action: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType),
        nullable=False,
        index=True,
    )

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    room_id: Mapped[int | None] = mapped_column(
        ForeignKey("rooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
        index=True,
    )
