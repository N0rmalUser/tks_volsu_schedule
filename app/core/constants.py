from pathlib import Path

import pytz

from app.core.config import config


# ===== TIMEZONE =====
TZ = pytz.timezone(config.timezone)

# ===== PATHS =====
ROOT_PATH = Path(__file__).resolve().parent.parent.parent

DATA_PATH = ROOT_PATH / "data"
GROUPS_SCHEDULE_PATH = DATA_PATH / "groups"
TEACHERS_SHEETS_PATH = DATA_PATH / "teachers"
ROOMS_SHEETS_PATH = DATA_PATH / "rooms"

PLOT_PATH = DATA_PATH / "plot"
