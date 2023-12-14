import json
teacher_json = None
group_json = None
room_json = None
message_counter = {}
teacher = {}
group = {}
user = {}
week = {}
room = {}
day = {}
msg = {}


def get_topic_id(user_id):
    with open("data\\topic_id.json", "r", encoding="utf-8") as file:
        user = json.load(file)
        return user[user_id]["topic_id"]


def set_topic_id(user_id, topic_id):
    with open("data\\topic_id.json", 'r+') as file:
        data = json.load(file)
        data[user_id] = topic_id
    with open("data\\topic_id.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_user_type(user_id):
    with open('jsons\\teachers.json', 'r', encoding='utf-8') as file:
        user_type = json.load(file)
    return user_type[user_id]


def get_view_setting(user_id):
    with open('data\\view_settings.json', 'r', encoding='utf-8') as file:
        view_setting = json.load(file)
    return view_setting[str(user_id)]


def set_view_setting(user_id, setting):
    with open('data\\view_settings.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        data[user_id] = setting
    with open("data\\view_settings.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def open_files():
    global teacher_json, group_json, room_json
    with open('jsons\\teachers.json', 'r', encoding='utf-8') as file:
        teacher_json = json.load(file)
    with open('jsons\\groups.json', 'r', encoding='utf-8') as file:
        group_json = json.load(file)
    with open('jsons\\rooms.json', 'r', encoding='utf-8') as file:
        room_json = json.load(file)


days = {
    "1": "Понедельник",
    "2": "Вторник",
    "3": "Среда",
    "4": "Четверг",
    "5": "Пятница",
    "6": "Суббота"
}
weeks = {
    "0": "Числитель",
    "1": "Знаменатель"
}
rooms = {
    "1-19m": "1-19М",
    "2-01k": "2-01К",
    "2-06m": "2-06М",
    "2-13m": "2-13М",
    "2-17m": "2-17М",
    "3-15k": "3-15К",
    "3-16k": "3-16К",
}