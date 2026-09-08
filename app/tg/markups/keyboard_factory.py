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

from aiogram.filters.callback_data import CallbackData

from app.schemas.enums import Keyboard, WeekType


class ChangeCallbackFactory(CallbackData, prefix="start"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: str | None
    value: int


class DayCallbackFactory(CallbackData, prefix="common"):
    """Фабрика для создания CallbackData для клавиатур изменения дня или недели."""

    action: str | None = None
    value: int
    day: int | None = None
    week: WeekType | None = None
    keyboard: Keyboard | None = None


class DefaultChangeCallbackFactory(CallbackData, prefix="default"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: str | None = None
    value: int
