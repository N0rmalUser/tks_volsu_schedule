from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

student_menu = [
    [
        KeyboardButton(text="Расписание на сегодня")
    ], [
        KeyboardButton(text="Группы")
    ]
]
teacher_menu = [
    [
        KeyboardButton(text="Расписание на сегодня")
    ], [
        KeyboardButton(text="Группы"),
        KeyboardButton(text="Преподаватели"),
        KeyboardButton(text="Кабинеты")
    ]
]
rooms = [
    [
        InlineKeyboardButton(text="1-19М", callback_data="room-1-19m"),
        InlineKeyboardButton(text="2-01K", callback_data="room-2-01k")
    ], [
        InlineKeyboardButton(text="2-06М", callback_data="room-2-06m"),
        InlineKeyboardButton(text="2-13М", callback_data="room-2-13m"),
        InlineKeyboardButton(text="2-17М", callback_data="room-2-17m")
    ], [
        InlineKeyboardButton(text="3-15К", callback_data="room-3-15k"),
        InlineKeyboardButton(text="3-16К", callback_data="room-3-16k")
    ], [
        InlineKeyboardButton(text="добавлю позже", callback_data="ignore")
    ]
]
groups = [
    [
        InlineKeyboardButton(text="ИТСм-231", callback_data="group-ИТСм-231"),
        InlineKeyboardButton(text="ИТСм-221", callback_data="group-ИТСм-221")
    ], [
        InlineKeyboardButton(text="ИБТС-231", callback_data="group-ИБТС-231"),
        InlineKeyboardButton(text="ИБТС-221", callback_data="group-ИБТС-221"),
        InlineKeyboardButton(text="ИБТС-211", callback_data="group-ИБТС-211")
    ], [
        InlineKeyboardButton(text="ИТСб-231", callback_data="group-ИТСб-231"),
        InlineKeyboardButton(text="ИТСб-221", callback_data="group-ИТСб-221"),
        InlineKeyboardButton(text="ИТСб-211", callback_data="group-ИТСб-211"),
        InlineKeyboardButton(text="ИТСб-201", callback_data="group-ИТСб-201")
    ], [
        InlineKeyboardButton(text="РСК-231", callback_data="group-РСК-231"),
        InlineKeyboardButton(text="РСК-221", callback_data="group-РСК-221"),
        InlineKeyboardButton(text="РСК-211", callback_data="group-РСК-211"),
        InlineKeyboardButton(text="РСК-201", callback_data="group-РСК-201")
    ]
]
teachers = [
    [
        InlineKeyboardButton(text="Арепьева Е.Е.", callback_data="teacher-Арепьева Е.Е."),
        InlineKeyboardButton(text="Безбожнов О.Н.", callback_data="teacher-Безбожнов О.Н.")
    ], [
        InlineKeyboardButton(text="Василюк Д.И.", callback_data="teacher-Василюк Д.И."),
        InlineKeyboardButton(text="Галич С.В.", callback_data="teacher-Галич С.В.")
    ], [
        InlineKeyboardButton(text="Гомазкова Л.К.", callback_data="teacher-Гомазкова Л.К."),
        InlineKeyboardButton(text="Дмитриенко Н.Р.", callback_data="teacher-Дмитриенко Н.Р.")
    ], [
        InlineKeyboardButton(text="Елфимова О.И.", callback_data="teacher-Елфимова О.И."),
        InlineKeyboardButton(text="Ермакова Н.Н.", callback_data="teacher-Ермакова Н.Н.")
    ], [
        InlineKeyboardButton(text="Задорожнева Ю.В.", callback_data="teacher-Задорожнева Ю.В."),
        InlineKeyboardButton(text="Карташевский В.Г.", callback_data="teacher-Карташевский В.Г.")
    ], [
        InlineKeyboardButton(text="Пономарев И.Н.", callback_data="teacher-Пономарев И.Н."),
        InlineKeyboardButton(text="Ромасевич Е.П.", callback_data="teacher-Ромасевич Е.П.")
    ], [
        InlineKeyboardButton(text="Ромасевич П.В.", callback_data="teacher-Ромасевич П.В."),
        InlineKeyboardButton(text="Сафонова О.Е.", callback_data="teacher-Сафонова О.Е.")
    ], [
        InlineKeyboardButton(text="Семенов Е.С.", callback_data="teacher-Семенов Е.С."),
        InlineKeyboardButton(text="Стебенькова Н.А.", callback_data="teacher-Стебенькова Н.А.")
    ], [
        InlineKeyboardButton(text="Тюхтяев Д.А.", callback_data="teacher-Тюхтяев Д.А."),
        InlineKeyboardButton(text="Стебеньков А.М.", callback_data="teacher-Стебеньков А.М.")
    ], [
        InlineKeyboardButton(text="Чадаев Д.И.", callback_data="teacher-Чадаев Д.И."),
        InlineKeyboardButton(text="Черных С.В.", callback_data="teacher-Черных С.В.")
    ]
]

group_week0 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/group/0/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/group/0/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/group/0/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/group/0/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/group/0/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/group/0/6")
    ],
    [
        InlineKeyboardButton(text="✅ Числитель", callback_data="ignore"),
        InlineKeyboardButton(text="Знаменатель ➡️", callback_data="week-group-1")
    ]
]
group_week1 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/group/1/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/group/1/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/group/1/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/group/1/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/group/1/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/group/1/6")
    ],
    [
        InlineKeyboardButton(text="✅ Знаменатель", callback_data="ignore"),
        InlineKeyboardButton(text="Числитель ➡️", callback_data="week-group-0")
    ]
]

teacher_week0 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/teacher/0/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/teacher/0/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/teacher/0/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/teacher/0/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/teacher/0/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/teacher/0/6")
    ],
    [
        InlineKeyboardButton(text="✅ Числитель", callback_data="ignore"),
        InlineKeyboardButton(text="Знаменатель ➡️", callback_data="week-teacher-1")
    ]
]
teacher_week1 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/teacher/1/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/teacher/1/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/teacher/1/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/teacher/1/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/teacher/1/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/teacher/1/6")
    ],
    [
        InlineKeyboardButton(text="✅ Знаменатель", callback_data="ignore"),
        InlineKeyboardButton(text="Числитель ➡️", callback_data="week-teacher-0")
    ]
]
room_week0 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/room/0/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/room/0/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/room/0/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/room/0/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/room/0/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/room/0/6")
    ],
    [
        InlineKeyboardButton(text="✅ Числитель", callback_data="ignore"),
        InlineKeyboardButton(text="Знаменатель ➡️", callback_data="week-room-1")
    ]
]
room_week1 = [
    [
        InlineKeyboardButton(text="Пн", callback_data="day/room/1/1"),
        InlineKeyboardButton(text="Вт", callback_data="day/room/1/2"),
        InlineKeyboardButton(text="Ср", callback_data="day/room/1/3")
    ], [
        InlineKeyboardButton(text="Чт", callback_data="day/room/1/4"),
        InlineKeyboardButton(text="Пт", callback_data="day/room/1/5"),
        InlineKeyboardButton(text="Сб", callback_data="day/room/1/6")
    ], [
        InlineKeyboardButton(text="✅ Знаменатель", callback_data="ignore"),
        InlineKeyboardButton(text="Числитель ➡️", callback_data="week-room-0")
    ]
]
view = [
    [
        InlineKeyboardButton(text="Картинка", callback_data="view_image")
    ], [
        InlineKeyboardButton(text="Текст", callback_data="view_text")
    ]
]

group_week0 = InlineKeyboardMarkup(inline_keyboard=group_week0)
group_week1 = InlineKeyboardMarkup(inline_keyboard=group_week1)

teacher_week0 = InlineKeyboardMarkup(inline_keyboard=teacher_week0)
teacher_week1 = InlineKeyboardMarkup(inline_keyboard=teacher_week1)

room_week0 = InlineKeyboardMarkup(inline_keyboard=room_week0)
room_week1 = InlineKeyboardMarkup(inline_keyboard=room_week1)

rooms = InlineKeyboardMarkup(inline_keyboard=rooms)
groups = InlineKeyboardMarkup(inline_keyboard=groups)
teachers = InlineKeyboardMarkup(inline_keyboard=teachers)

view = InlineKeyboardMarkup(inline_keyboard=view)

student_menu = ReplyKeyboardMarkup(keyboard=student_menu, resize_keyboard=True)
teacher_menu = ReplyKeyboardMarkup(keyboard=teacher_menu, resize_keyboard=True)
