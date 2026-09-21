import locale
import platform


def setup_locale() -> None:
    locale_name = "Russian_Russia.1251" if platform.system() == "Windows" else "ru_RU.UTF-8"

    try:
        locale.setlocale(locale.LC_TIME, locale_name)
    except locale.Error:
        locale.setlocale(locale.LC_TIME, "")
