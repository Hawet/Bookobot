from aiogram.dispatcher.filters.state import State, StatesGroup



class BinderStates(StatesGroup):
    """
    Class that defines binder state group
    """
    main_menu = State()
    like_book = State()
    dislike_book = State()

