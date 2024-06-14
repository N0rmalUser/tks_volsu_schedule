from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_menu = [
    [
        KeyboardButton(text="/log clear"),
        KeyboardButton(text="/log send"),
        KeyboardButton(text="/send_db")
     ],
    [
        KeyboardButton(text="/track start"),
        KeyboardButton(text="/track stop"),
        KeyboardButton(text="/track status")
    ],
    [
        KeyboardButton(text="/send_schedule"),
        KeyboardButton(text="/dump"),
        KeyboardButton(text="/info")
    ],
    [
        KeyboardButton(text="/hours_stat"),
        KeyboardButton(text="/days_stat")
    ]
]

admin_menu = ReplyKeyboardMarkup(keyboard=admin_menu, resize_keyboard=True)
