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
        KeyboardButton(text="/заглушка"),
        KeyboardButton(text="/info")
     ]
]

admin_menu = ReplyKeyboardMarkup(keyboard=admin_menu, resize_keyboard=True)
