from typing import cast

from app.core.config import config
from app.database.models import Group, Room, Schedule, Subject, Teacher
from app.database.repository.directory import DirectoryRepository
from app.database.repository.schedule import ScheduleRepository
from app.database.session import session_scope
from app.schemas.enums import GroupType, WeekType
from app.schemas.schedule import ScheduleEntry, ScheduleRow


class ScheduleService:
    async def init_schedule(self) -> None:
        async with session_scope() as session:
            repository = DirectoryRepository(session)

            groups = sorted([group for group in config.groups if group != "-"])
            personal = sorted([students for students in config.students if students not in config.teachers])

            await repository.add_groups([Group(name=name) for name in groups])
            await repository.add_teachers([Teacher(name=name) for name in config.teachers])
            await repository.add_teachers([Teacher(name=name) for name in personal])
            await repository.add_rooms([Room(name=name) for name in config.rooms])
            await session.flush()

    async def import_schedule(
        self,
        rows: list[ScheduleRow],
        group_type: GroupType,
    ) -> None:
        if not rows:
            raise ValueError("Расписание пустое")

        async with session_scope() as session:
            schedule_repository = ScheduleRepository(session)
            directory_repository = DirectoryRepository(session)

            await schedule_repository.clear_schedule(group_type=group_type)

            group_names = {row.group for row in rows if row.group}
            teacher_names = {row.teacher for row in rows if row.teacher}
            subject_names = {row.subject for row in rows if row.subject}
            room_names = {row.room for row in rows if row.room}

            groups = await directory_repository.get_groups(names=group_names)
            teachers = await directory_repository.get_teachers(names=teacher_names)
            rooms = await directory_repository.get_rooms(names=room_names)
            subjects = await directory_repository.get_subjects(names=subject_names)

            groups = {group.name: group for group in groups}
            teachers = {teacher.name: teacher for teacher in teachers}
            rooms = {room.name: room for room in rooms}
            subjects = {subject.name: subject for subject in subjects}

            new_groups = [Group(name=name) for name in group_names if name not in groups]
            new_teachers = [Teacher(name=name) for name in teacher_names if name not in teachers]
            new_rooms = [Room(name=name) for name in room_names if name not in rooms]
            new_subjects = [Subject(name=name) for name in subject_names if name not in subjects]

            await directory_repository.add_groups(new_groups)
            await directory_repository.add_teachers(new_teachers)
            await directory_repository.add_subjects(new_subjects)
            await directory_repository.add_rooms(new_rooms)

            groups.update({group.name: group for group in new_groups})
            teachers.update({teacher.name: teacher for teacher in new_teachers})
            subjects.update({subject.name: subject for subject in new_subjects})
            rooms.update({room.name: room for room in new_rooms})
            await session.flush()

            entries = [
                Schedule(
                    group_id=groups[row.group].id,
                    group_type=group_type,
                    teacher_id=(teachers[row.teacher].id if row.teacher else None),
                    subject_id=subjects[row.subject].id,
                    room_id=rooms[row.room].id if row.room else None,
                    day_of_week=row.day_of_week,
                    lesson_number=row.lesson_number,
                    week_type=row.week_type,
                    subgroup=row.subgroup,
                )
                for row in rows
            ]

            await schedule_repository.add_schedule(entries)

    async def get_group_schedule(
        self,
        *,
        group_id: int,
        day_of_week: int,
        week: WeekType,
        subgroup: int | None = None,
    ) -> tuple[str, list[ScheduleEntry]]:
        async with session_scope() as session:
            schedule_repository = ScheduleRepository(session)
            directory_repository = DirectoryRepository(session)
            group = await directory_repository.get_group_by_id(group_id)

            if group is None or group.name is None:
                return "Нет такой группы", []

            group_name = cast("str", cast("object", group.name))

            schedules = await schedule_repository.get_group_schedule(
                group_id=group_id,
                day_of_week=day_of_week,
                week_type=week,
                subgroup=subgroup,
            )

            entries = [
                ScheduleEntry(
                    lesson_number=s.lesson_number,
                    day_of_week=s.day_of_week,
                    week_type=s.week_type,
                    subject=s.subject.name if s.subject else None,
                    teacher=s.teacher.name if s.teacher else None,
                    room=s.room.name if s.room else None,
                    group=group_name,
                    subgroup=s.subgroup,
                )
                for s in schedules
            ]

            return group_name, entries

    async def get_teacher_schedule(
        self,
        *,
        teacher_id: int,
        day_of_week: int,
        week: WeekType,
    ) -> tuple[str, list[ScheduleEntry]]:
        async with session_scope() as session:
            schedule_repository = ScheduleRepository(session)
            directory_repository = DirectoryRepository(session)
            teacher = await directory_repository.get_teacher_by_id(teacher_id)

            if teacher is None or teacher.name is None:
                return "Нет такого преподавателя", []

            teacher_name = cast("str", cast("object", teacher.name))

            schedules = await schedule_repository.get_teacher_schedule(
                teacher_id=teacher_id,
                day_of_week=day_of_week,
                week_type=week,
            )

            entries = [
                ScheduleEntry(
                    lesson_number=s.lesson_number,
                    day_of_week=s.day_of_week,
                    week_type=s.week_type,
                    subject=s.subject.name if s.subject else None,
                    teacher=teacher_name,
                    room=s.room.name if s.room else None,
                    group=s.group.name if s.group else None,
                    subgroup=s.subgroup,
                )
                for s in schedules
            ]

            return teacher_name, entries

    async def get_room_schedule(
        self,
        *,
        room_id: int,
        day_of_week: int,
        week: WeekType,
    ) -> tuple[str, list[ScheduleEntry]]:
        async with session_scope() as session:
            schedule_repository = ScheduleRepository(session)
            directory_repository = DirectoryRepository(session)
            room = await directory_repository.get_room_by_id(room_id)

            if room is None or room.name is None:
                return "Нет такой аудитории", []

            room_name = cast("str", cast("object", room.name))

            schedules = await schedule_repository.get_room_schedule(
                room_id=room_id,
                room_name=room_name,
                day_of_week=day_of_week,
                week_type=week,
            )

            entries = [
                ScheduleEntry(
                    lesson_number=s.lesson_number,
                    day_of_week=s.day_of_week,
                    week_type=s.week_type,
                    subject=s.subject.name if s.subject else None,
                    teacher=s.teacher.name if s.teacher else None,
                    room=s.room.name if s.room else room_name,
                    group=s.group.name if s.group else None,
                    subgroup=s.subgroup,
                )
                for s in schedules
            ]

            return room_name, entries

    def _parse_student_group(self, value: str) -> tuple[str, int | None]:
        if "." not in value:
            return value, None

        group, subgroup = value.rsplit(".", 1)

        return group, int(subgroup)

    async def get_teacher_full_schedule(
        self,
        *,
        teacher_id: int,
        day_of_week: int,
        week: WeekType,
    ) -> tuple[str, list[tuple[ScheduleEntry, bool]]]:
        teacher_name, teacher_entries = await self.get_teacher_schedule(
            teacher_id=teacher_id,
            day_of_week=day_of_week,
            week=week,
        )
        student_group = config.students.get(teacher_name)

        if student_group is None:
            teacher_entries = [(e, True) for e in teacher_entries]
            return teacher_name, teacher_entries

        group_name, subgroup = self._parse_student_group(student_group)
        group_ids = await self.get_group_ids([group_name])

        _, group_entries = await self.get_group_schedule(
            group_id=int(group_ids[group_name]),
            subgroup=subgroup,
            day_of_week=day_of_week,
            week=week,
        )

        entries = [(entry, True) for entry in teacher_entries] + [(entry, False) for entry in group_entries]

        entries.sort(
            key=lambda x: (
                x[0].lesson_number,
                0 if x[0].subgroup is None else x[0].subgroup,
            )
        )
        return teacher_name, entries

    async def get_teacher_ids(
        self,
        teacher_names: list[str] = config.all_personal,
    ) -> dict[str, int]:
        async with session_scope() as session:
            directory_repository = DirectoryRepository(session)
            teachers = await directory_repository.get_teachers(teacher_names)
            return {teacher.name: teacher.id for teacher in teachers}

    async def get_teacher_name(
        self,
        teacher_id: int,
    ) -> str:
        async with session_scope() as session:
            directory_repository = DirectoryRepository(session)
            teacher = await directory_repository.get_teacher_by_id(teacher_id)
            if teacher is None or teacher.name is None:
                return "Такого преподавателя не существует"
            return cast("str", cast("object", teacher.name))

    async def get_group_ids(self, group_names: list[str]) -> dict[str, int]:
        async with session_scope() as session:
            directory_repository = DirectoryRepository(session)
            groups = await directory_repository.get_groups(group_names)
            return {group.name: group.id for group in groups}

    async def get_group_name(self, group_id: int) -> str:
        async with session_scope() as session:
            directory_repository = DirectoryRepository(session)
            group = await directory_repository.get_group_by_id(group_id)
            if group is None or group.name is None:
                return "Такой группы не существует"
            return cast("str", cast("object", group.name))

    async def get_room_name(self, room_id: int) -> str:
        async with session_scope() as session:
            directory_repository = DirectoryRepository(session)
            room = await directory_repository.get_room_by_id(room_id)
            if room is None or room.name is None:
                return "Такой аудитории не существует"
            return cast("str", cast("object", room.name))
