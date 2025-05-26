from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.texts.buttons import MAIN_MENU_KB_TEXT
from app.texts.callback_datas import GET_DATES_CBD

main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=MAIN_MENU_KB_TEXT, callback_data=GET_DATES_CBD)
    ]
])