from __future__ import annotations

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.schemas.enums import GroupType, WeekType


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    schedule: Mapped[list[Schedule]] = relationship(
        back_populates="group",
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    schedule: Mapped[list[Schedule]] = relationship(
        back_populates="teacher",
    )


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    schedule: Mapped[list[Schedule]] = relationship(
        back_populates="room",
    )


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    schedule: Mapped[list[Schedule]] = relationship(
        back_populates="subject",
    )


class Schedule(Base):
    __tablename__ = "schedule"

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "subgroup",
            "teacher_id",
            "week_type",
            "day_of_week",
            "lesson_number",
            name="uq_schedule_entry",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    group_type: Mapped[GroupType] = mapped_column(
        Enum(GroupType),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey(
            "groups.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    subgroup: Mapped[int | None] = mapped_column(
        Integer,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey(
            "subjects.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "teachers.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=True,
    )

    room_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "rooms.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=True,
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    lesson_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    week_type: Mapped[WeekType] = mapped_column(
        Enum(WeekType),
        default=WeekType.EVERY,
    )

    group: Mapped[Group] = relationship(
        back_populates="schedule",
    )

    subject: Mapped[Subject] = relationship(
        back_populates="schedule",
    )

    teacher: Mapped[Teacher | None] = relationship(back_populates="schedule")

    room: Mapped[Room | None] = relationship(back_populates="schedule")
