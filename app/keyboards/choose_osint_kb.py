from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.texts.buttons import OSINT_1_TEXT, OSINT_2_TEXT, OSINT_3_TEXT
from app.texts.callback_datas import OSINT_DYXLESS_CBD

choose_osint_ikb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text=OSINT_1_TEXT, callback_data=OSINT_DYXLESS_CBD)
    ]
])