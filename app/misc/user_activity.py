# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime, timedelta
from math import ceil

import matplotlib.pyplot as plt
import pandas as pd
from lets_plot import *
from pytz import timezone as tz

import app.database.activity as db
from app.config import TIMEZONE


def plot_user_activity_by_hours(date_string=None):
    """Строит и сохраняет график активности пользователей по часам за определённый день по часам."""

    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=["date", "hour", "user_count"])

    selected_date = (
        datetime.strptime(date_string, "%d.%m.%y").date()
        if date_string
        else datetime.now(tz(TIMEZONE)).date()
    )

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y").dt.date
    df_selected_date = df[df["date"] == selected_date]

    hourly_activity = (
        df_selected_date.groupby("hour")["user_count"].sum().reindex(range(24), fill_value=0)
    )
    max_value = ceil(hourly_activity.max() / 10) * 10

    plt.figure(figsize=(11, 5))
    hourly_activity.plot(kind="bar")
    plt.xlabel("Часы")
    plt.ylabel("Количество юзверей")
    date_label = selected_date.strftime("%d.%m.%Y")
    plt.title(f"Активность юзверей на {date_label} по часам")
    plt.yticks(range(0, max_value + 10, 10))
    plt.xticks(range(24), [f"{h:02d}:00" for h in range(24)], rotation=45)
    for i, v in enumerate(hourly_activity):
        if v != 0:
            plt.text(i, v + 0.5, str(v), ha="center", va="bottom")
    plt.tight_layout()

    plt.savefig("data/user_activity_by_hours.png")
    plt.close()


def html_plot_user_activity_by_hours(date_string=None):
    """Строит и сохраняет график активности пользователей по дням за последние 30 дней."""

    LetsPlot.setup_html(no_js=True)
    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=["date", "hour", "user_count"])
    selected_date = (
        datetime.strptime(date_string, "%d.%m.%y").date()
        if date_string
        else datetime.now(tz(TIMEZONE)).date()
    )
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y").dt.date
    df_selected_date = df[df["date"] == selected_date].copy()
    df_selected_date["hour"] = (
        df_selected_date["hour"].astype(str).apply(lambda x: f"{int(x):02d}:00")
    )
    hourly_activity = (
        df_selected_date.groupby("hour")["user_count"]
        .sum()
        .reindex([f"{h:02d}:00" for h in range(24)], fill_value=0)
    )
    background = element_rect(fill="#14181e")
    (
        ggplot(hourly_activity.reset_index(), aes(x="hour", y="user_count"))
        + ggsize(1000, 500)
        + geom_bar(stat="identity", fill="blue")
        + ggtitle("Активность юзверей по часам", str(selected_date))
        + xlab("Время")
        + ylab("Количество юзверей")
        + scale_y_continuous(breaks=list(range(0, ceil(hourly_activity.max()) * 10)))
        + flavor_high_contrast_dark()
        + theme(
            axis_text_x=element_text(hjust=1, angle=45),
            panel_grid_major_x="blank",
            plot_background=background,
            plot_title=element_text(),
        )
    ).to_html("data/user_activity_by_hours.html")


def plot_user_activity_by_days():
    """Строит и сохраняет график активности пользователей по дням за последние 30 дней."""

    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=["date", "hour", "user_count"])
    today = datetime.now(tz(TIMEZONE)).date()
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

    date_range = [today - timedelta(days=i) for i in range(29, -1, -1)]
    daily_activity = df.groupby("date")["user_count"].sum().reindex(date_range, fill_value=0)
    max_value = ceil(daily_activity.max() / 10) * 10

    plt.figure(figsize=(11, 5))

    daily_activity.plot(kind="bar")
    plt.xlabel("Дата")
    plt.ylabel("Количество юзверей")
    plt.title("Активность юзверей по дням")
    plt.yticks(range(0, max_value + 10, 10))
    plt.xticks(rotation=45)

    date_labels = [date.strftime("%d-%m") for date in daily_activity.index]
    plt.xticks(range(len(date_labels)), date_labels, rotation=45)

    for i, v in enumerate(daily_activity):
        if v != 0:
            plt.text(i, v, str(v), ha="center", va="bottom")
    plt.tight_layout()

    plt.savefig("data/user_activity_by_days.png")
    plt.close()


def html_plot_user_activity_by_days():
    """Строит и сохраняет график активности пользователей по дням за последние 30 дней."""

    LetsPlot.setup_html(no_js=True)
    df = pd.DataFrame(db.fetch_user_activity_stats(), columns=["date", "hour", "user_count"])
    today = datetime.now(tz(TIMEZONE)).date()
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")

    date_range = [today - timedelta(days=i) for i in range(29, -1, -1)]
    daily_activity = df.groupby("date")["user_count"].sum().reindex(date_range, fill_value=0)
    daily_activity.index = pd.DatetimeIndex(daily_activity.index).strftime("%d-%m")

    background = element_rect(fill="#14181e")

    (
        ggplot(daily_activity.reset_index(), aes(x="date", y="user_count"))
        + ggsize(1000, 500)
        + geom_bar(stat="identity", fill="blue")
        + ggtitle(
            "Активность юзверей по дням",
            f"С {date_range[0].strftime('%d-%m-%Y')} по {date_range[-1].strftime('%d-%m-%Y')}",
        )
        + xlab("Дата")
        + ylab("Количество юзверей")
        + scale_y_continuous(breaks=list(range(0, ceil(daily_activity.max()) * 10)))
        + flavor_high_contrast_dark()
        + theme(
            axis_text_x=element_text(angle=70, hjust=1),
            panel_grid_major_x="blank",
            plot_background=background,
            plot_title=element_text(),
        )
    ).to_html("data/user_activity_by_days.html")
