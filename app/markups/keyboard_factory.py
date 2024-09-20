# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ChangeCallbackFactory(CallbackData, prefix="start_change"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: Optional[str] = None
    value: Optional[int] = None


class DayCallbackFactory(CallbackData, prefix="day_change"):
    """Фабрика для создания CallbackData для клавиатур изменения дня или недели."""

    action: Optional[str] = None
    value: Optional[int] = None
    day: Optional[int] = None
    week: Optional[int] = None
    keyboard_type: Optional[str] = None


class DefaultChangeCallbackFactory(CallbackData, prefix="default_change"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: Optional[str] = None
    value: Optional[int] = None


class ScheduleEditingCallbackFactory(CallbackData, prefix="edit"):
    """Фабрика для создания CallbackData для клавиатур изменения расписания."""

    action: Optional[str] = None
    value: Optional[int] = None
    day: Optional[int] = None
    edit: Optional[str] = None
    schedule_id: Optional[int] = None
    keyboard_type: Optional[str] = None


class ScheduleConstructorCallbackFactory(CallbackData, prefix="add"):
    """Фабрика для создания CallbackData для клавиатур изменения расписания."""

    action: Optional[str] = None
    value: Optional[int] = None
    add: Optional[str] = None
    schedule_id: Optional[int] = None
    keyboard_type: Optional[str] = None
    previous: Optional[str] = None
