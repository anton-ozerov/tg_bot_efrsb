from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.texts.buttons import CANCEL_TEXT
from app.texts.callback_datas import BACK_TO_MAIN_MENU_CDD

back_main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=CANCEL_TEXT, callback_data=BACK_TO_MAIN_MENU_CDD)
    ]
])