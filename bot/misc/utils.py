import sqlite3
from functools import wraps


def sql_kit(db=":memory:"):
    """
    Декоратор для работы с базой данных. Он открывает соединение с базой данных, выполняет функцию и закрывает соединение.
    :param db:  путь к базе данных
    :return:  результат выполнения функции
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db)
            try:
                result = func(*args, **kwargs, cursor=conn.cursor())
                conn.commit()
                return result
            finally:
                conn.close()

        return wrapper

    return decorator
