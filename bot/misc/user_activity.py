import bot.database as db

from config import timezone

from datetime import datetime, timedelta

from math import ceil
import matplotlib.pyplot as plt
import pandas as pd
from pytz import timezone as tz


def plot_user_activity_by_hours(date_string=None):
    """Строит и сохраняет график активности пользователей по часам за определённый день по часам."""

    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=['date', 'hour', 'user_count'])

    selected_date = datetime.strptime(date_string, '%d.%m.%y').date() \
        if date_string \
        else datetime.now(tz(timezone)).date()

    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.date
    df_selected_date = df[df['date'] == selected_date]

    hourly_activity = df_selected_date.groupby('hour')['user_count'].sum().reindex(range(24), fill_value=0)
    max_value = ceil(hourly_activity.max() / 10) * 10

    plt.figure(figsize=(11, 5))
    hourly_activity.plot(kind='bar')
    plt.xlabel('Часы')
    plt.ylabel('Количество юзверей')
    date_label = selected_date.strftime('%d.%m.%Y')
    plt.title(f'Активность юзверей на {date_label} по часам')
    plt.yticks(range(0, max_value + 10, 10))
    plt.xticks(range(24), [f'{h:02d}:00' for h in range(24)], rotation=45)
    for i, v in enumerate(hourly_activity):
        if v != 0:
            plt.text(i, v + 0.5, str(v), ha='center', va='bottom')
    plt.tight_layout()

    plt.savefig('data/user_activity_by_hours.png')
    plt.close()


def plot_user_activity_by_days():
    """Строит и сохраняет график активности пользователей по дням за последние 30 дней."""

    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=['date', 'hour', 'user_count'])
    today = datetime.now(tz(timezone)).date()
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    date_range = [today - timedelta(days=i) for i in range(29, -1, -1)]
    daily_activity = df.groupby('date')['user_count'].sum().reindex(date_range, fill_value=0)
    max_value = ceil(daily_activity.max() / 10) * 10

    plt.figure(figsize=(11, 5))

    daily_activity.plot(kind='bar')
    plt.xlabel('Дата')
    plt.ylabel('Количество юзверей')
    plt.title('Активность юзверей по дням')
    plt.yticks(range(0, max_value + 10, 10))
    plt.xticks(rotation=45)

    date_labels = [date.strftime('%d-%m') for date in daily_activity.index]
    plt.xticks(range(len(date_labels)), date_labels, rotation=45)

    for i, v in enumerate(daily_activity):
        if v != 0:
            plt.text(i, v, str(v), ha='center', va='bottom')
    plt.tight_layout()

    plt.savefig('data/user_activity_by_days.png')
    plt.close()
