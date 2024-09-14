from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


# Функция быстрого создания кнопок в боте
def keyboards_game(list_button: list):
    """
    :param list_button: Список кнопок
    :return: Получаем клавиатуру
    """
    list_b = [KeyboardButton(text=name) for name in list_button]
    kb = ReplyKeyboardMarkup(keyboard=[list_b], resize_keyboard=True, one_time_keyboard=True)
    return kb

# Функция быстрого создания инлайн кнопок в боте
def ikb(list_text, list_callback):
    """
    :param list_text: Передаем название кнопок
    :param list_callback: Передаем их вызовы
    :return: Получаем клавиатуру
    """
    list_button = []
    for i in range(0, len(list_text)):
        button = InlineKeyboardButton(text=list_text[i], callback_data=list_callback[i])
        list_button.append(button)

    return InlineKeyboardMarkup(inline_keyboard=[list_button])

