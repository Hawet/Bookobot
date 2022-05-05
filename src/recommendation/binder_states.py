from aiogram.dispatcher.filters.state import State, StatesGroup



class BinderStates(StatesGroup):
    """
    Class that defines binder state group
    """

    def __init__(self) -> None:
        self.main_menu = State()
        self.like_book = State()
        self.dislike_book = State()

