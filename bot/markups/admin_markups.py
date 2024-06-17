from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_menu = [
    [
        KeyboardButton(text="/track start"),
        KeyboardButton(text="/track stop"),
        KeyboardButton(text="/track status")
    ],
    [
        KeyboardButton(text="/days_stat"),
        KeyboardButton(text="/hours_stat")
    ],
    [
        KeyboardButton(text="/dump"),
        KeyboardButton(text="/info")
    ]
]

admin_menu = ReplyKeyboardMarkup(keyboard=admin_menu, resize_keyboard=True)
