from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    waiting_for_confirmation = State()
    sending_messages = State()
    cancel_sending = State()
