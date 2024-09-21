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

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_menu = [
    [
        KeyboardButton(text="/log"),
        KeyboardButton(text="/track stop"),
        KeyboardButton(text="/track status"),
    ],
    [KeyboardButton(text="/month_stat"), KeyboardButton(text="/day_stat")],
    [KeyboardButton(text="/dump"), KeyboardButton(text="/info")],
]

admin_menu = ReplyKeyboardMarkup(keyboard=admin_menu, resize_keyboard=True)
