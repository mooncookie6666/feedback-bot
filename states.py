from aiogram.dispatcher.filters.state import State, StatesGroup

class Feedback(StatesGroup):
    source = State()
    date = State()
    review = State()
    contact = State()