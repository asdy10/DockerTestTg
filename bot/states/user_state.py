from aiogram.dispatcher.filters.state import StatesGroup, State


class NoticeState(StatesGroup):
    doc = State()
    filters = State()
    article = State()
    choice_store = State()
    agent = State()
    days = State()

    text = State()
    positions = State()


class QuestionState(StatesGroup):
    text = State()
    confirm = State()


class FeedbackState(StatesGroup):
    text = State()
    confirm = State()


class SetListName(StatesGroup):
    name = State()


class PostavkaState(StatesGroup):
    #seller = State()
    article = State()
    confirm = State()

