from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.schedule import Group, Teacher
from app.schemas.enums import Platform, UserRole


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint(
            "platform",
            "platform_user_id",
            name="uq_users_platform_platform_user_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    platform: Mapped[Platform] = mapped_column(
        Enum(Platform, native_enum=False),
        nullable=False,
    )

    platform_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.STUDENT,
        nullable=False,
    )

    tg_topic_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    tg_tracking: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"),
    )

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id"),
    )

    bot_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    default_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id"),
    )

    default_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    teacher: Mapped[Teacher | None] = relationship(
        foreign_keys=[teacher_id],
    )

    default_teacher: Mapped[Teacher | None] = relationship(
        foreign_keys=[default_teacher_id],
    )

    group: Mapped[Group | None] = relationship(
        foreign_keys=[group_id],
    )

    default_group: Mapped[Group | None] = relationship(
        foreign_keys=[default_group_id],
    )
