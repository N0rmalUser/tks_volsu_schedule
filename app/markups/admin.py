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

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/student"),
                KeyboardButton(text="/teacher"),
            ],
            [
                KeyboardButton(text="/log"),
                KeyboardButton(text="/track stop"),
                KeyboardButton(text="/track status"),
            ],
            [
                KeyboardButton(text="/dump"),
                KeyboardButton(text="/college"),
                KeyboardButton(text="/update"),
            ],
            [
                KeyboardButton(text="/month"),
                KeyboardButton(text="/day"),
                KeyboardButton(text="/info"),
            ],
        ],
        resize_keyboard=True,
    )


def cancel_sending():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отменить отправку", callback_data="cancel_sending")]]
    )


def message_confirm():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_all"),
            ],
            [
                InlineKeyboardButton(text="👫 Студентам", callback_data="confirm_students"),
                InlineKeyboardButton(text="👨‍🏫 Преподавателям", callback_data="confirm_teachers"),
            ],
            [InlineKeyboardButton(text="❌ Никому", callback_data="cancel_send")],
        ]
    )


def notify():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оповестить", callback_data="notify")],
        ]
    )
