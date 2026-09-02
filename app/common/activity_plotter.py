from datetime import date
from math import ceil

from lets_plot import (
    LetsPlot,
    aes,
    element_rect,
    element_text,
    flavor_high_contrast_dark,
    geom_bar,
    ggplot,
    ggsize,
    ggtitle,
    scale_y_continuous,
    theme,
    xlab,
    ylab,
)
from sqlalchemy.sql.schema import Sequence

from app.core.constants import PLOT_PATH
from app.schemas.activity import ActivityDayStat, ActivityHourStat


class ActivityPlotter:
    def __init__(self, output_path=PLOT_PATH):
        self.output_path = output_path

        LetsPlot.setup_html(no_js=True)

    @staticmethod
    def _get_y_max(values: Sequence[int]) -> int:
        maximum = max(values, default=0)

        if maximum == 0:
            return 10

        return max(10, ceil(maximum / 10) * 10)

    def save_day(
        self,
        stats: Sequence[ActivityHourStat],
        date: date,
    ) -> None:
        data = [
            {
                "Hour": stat.hour.strftime("%H"),
                "User Count": stat.user_count,
            }
            for stat in stats
        ]

        y_max = self._get_y_max(
            [item["User Count"] for item in data],
        )

        plot = (
            ggplot(data, aes(x="Hour", y="User Count"))
            + ggsize(1000, 500)
            + geom_bar(
                stat="identity",
                color="#cae6ff",
                fill="#cae6ff",
            )
            + ggtitle(f"Активность пользователей по часам на {date:%Y-%m-%d}")
            + xlab("Время")
            + ylab("Количество пользователей")
            + scale_y_continuous(
                limits=[0, y_max],
                breaks=list(
                    range(
                        0,
                        y_max + 1,
                        1 if y_max == 10 else 5,
                    )
                ),
            )
            + flavor_high_contrast_dark()
            + theme(
                axis_text_x=element_text(
                    angle=0,
                    hjust=0.5,
                ),
                panel_grid_major_x="blank",
                text=element_text(color="#d3e5f5"),
                plot_background=element_rect(fill="#122634"),
                plot_title=element_text(),
            )
        )

        plot.to_html(str(self.output_path / "activity_for_day.html"))

    def save_moth(
        self,
        stats: Sequence[ActivityDayStat],
        month: str,
    ) -> None:
        LetsPlot.setup_html(no_js=True)

        data = [
            {
                "Date": stat.date,
                "User Count": stat.user_count,
            }
            for stat in stats
        ]

        y_max = self._get_y_max(
            [item["User Count"] for item in data],
        )

        (
            ggplot(data, aes(x="Date", y="User Count"))
            + ggsize(1000, 500)
            + geom_bar(
                stat="identity",
                color="#cae6ff",
                fill="#cae6ff",
            )
            + ggtitle(f"Активность пользователей по дням с {month}")
            + xlab("Дата")
            + ylab("Количество пользователей")
            + scale_y_continuous(
                limits=[0, y_max],
                breaks=list(
                    range(
                        0,
                        y_max + 1,
                        1 if y_max == 10 else 5,
                    )
                ),
            )
            + flavor_high_contrast_dark()
            + theme(
                axis_text_x=element_text(
                    angle=0,
                    hjust=0.5,
                ),
                panel_grid_major_x="blank",
                text=element_text(color="#d3e5f5"),
                plot_background=element_rect(fill="#122634"),
                plot_title=element_text(),
            )
        ).to_html(str(PLOT_PATH / "activity_for_month.html"))
