from aiogram.filters.callback_data import CallbackData

from typing import Optional


class ChangeCallbackFactory(CallbackData, prefix='start_change'):
    action: Optional[str] = None
    value: Optional[str] = None


class DayCallbackFactory(CallbackData, prefix='day_change'):
    action: Optional[str] = None
    call_type: Optional[str] = None
    value: Optional[str] = None
