from data import schedules as sch
from datetime import datetime
import sqlite3
import json


def init_db():
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        topic_id TEXT,
        group_name TEXT,
        teacher_name TEXT,
        user_type TEXT,
        week TEXT,
        day TEXT,
        room TEXT
    )
    ''')
    conn.commit()
    conn.close()


def get_user_type(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_type FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_user_type(user_id, user_type):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, user_type) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET user_type=excluded.user_type;", (user_id, user_type))
    conn.commit()
    conn.close()


def get_teacher(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teacher_name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_teacher(user_id, teacher_name):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, teacher_name) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET teacher_name=excluded.teacher_name;", (user_id, teacher_name))
    conn.commit()
    conn.close()


def get_group(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT group_name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_group(user_id, group_name):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, group_name) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET group_name=excluded.group_name;", (user_id, group_name))
    conn.commit()
    conn.close()


def get_topic_id(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT topic_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_topic_id(user_id, topic_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, topic_id) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET topic_id=excluded.topic_id;", (user_id, topic_id))
    conn.commit()
    conn.close()


def get_week(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT week FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_week(user_id, week):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, week) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET week=excluded.week;", (user_id, week))
    conn.commit()
    conn.close()


def get_day(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT day FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_day(user_id, day):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, day) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET day=excluded.day;", (user_id, day))
    conn.commit()
    conn.close()


def get_room(user_id):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT room FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def set_room(user_id, room):
    conn = sqlite3.connect('data\\users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(user_id, room) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET room=excluded.room;", (user_id, room))
    conn.commit()
    conn.close()


def open_files():
    with open('data\\json_schedules\\teachers.json', 'r', encoding='utf-8') as file:
        sch.teacher_json = json.load(file)
    with open('data\\json_schedules\\groups.json', 'r', encoding='utf-8') as file:
        sch.group_json = json.load(file)
    with open('data\\json_schedules\\rooms.json', 'r', encoding='utf-8') as file:
        sch.room_json = json.load(file)


def set_today_date(user_id):
    set_day(user_id, f"{datetime.now().weekday() + 1}")
    set_week(user_id, "1" if datetime.now().isocalendar()[1] % 2 == 0 else "0")
