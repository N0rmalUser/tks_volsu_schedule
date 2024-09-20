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

from math import ceil

import pandas as pd
from lets_plot import *
from pandas import DataFrame


def plot_activity_for_day(df: pd.DataFrame, date: str):
    LetsPlot.setup_html(no_js=True)
    df["Hour"] = pd.to_datetime(df["Hour"], format="%Y-%m-%d %H:%M").dt.strftime("%H")

    y_max = ceil(df["User Count"].max() / 10) * 10
    background = element_rect(fill="#14181e")
    (
        ggplot(df, aes(x="Hour", y="User Count"))
        + ggsize(1000, 500)
        + geom_bar(stat="identity", fill="blue")
        + ggtitle(f"Активность пользователей по часам на {date}")
        + xlab("Время")
        + ylab("Количество пользователей")
        + scale_y_continuous(limits=[0, y_max], breaks=list(range(0, y_max + 1, 10)))
        + flavor_high_contrast_dark()
        + theme(
            panel_grid_major_x="blank",
            plot_background=background,
            plot_title=element_text(),
        )
    ).to_html("data/activity_for_day.html")


def plot_activity_for_month(df: DataFrame, month: str):
    LetsPlot.setup_html(no_js=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

    y_max = ceil(df["User Count"].max() / 10) * 10
    background = element_rect(fill="#14181e")
    (
        ggplot(df, aes(x="Date", y="User Count"))
        + ggsize(1000, 500)
        + geom_bar(stat="identity", fill="blue")
        + ggtitle(f"Активность пользователей по дням  {month}")
        + xlab("Дата")
        + ylab("Количество пользователей")
        + scale_y_continuous(limits=[0, y_max], breaks=list(range(0, y_max + 1, 10)))
        + flavor_high_contrast_dark()
        + theme(
            axis_text_x=element_text(angle=70, hjust=1),
            panel_grid_major_x="blank",
            plot_background=background,
            plot_title=element_text(),
        )
    ).to_html("data/activity_for_month.html")
