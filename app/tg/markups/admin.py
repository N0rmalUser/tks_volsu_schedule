from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/student"),
                KeyboardButton(text="/teacher"),
            ],
            [
                KeyboardButton(text="/track stop"),
                KeyboardButton(text="/menu"),
                KeyboardButton(text="/update"),
            ],
            [
                KeyboardButton(text="/info"),
            ],
        ],
        resize_keyboard=True,
    )
