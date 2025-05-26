import logging
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

from app.keyboards.get_dates_kb import main_menu_kb
from app.texts import messages
from app.texts.callback_datas import BACK_TO_MAIN_MENU_CDD


router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
@router.callback_query(F.data == BACK_TO_MAIN_MENU_CDD)
async def show_main_menu(msg_cbq: Message | CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()

    if isinstance(msg_cbq, Message):
        logger.info(f"Пользователь {msg_cbq.from_user.id} ввёл команду \\start")
        msg = await msg_cbq.answer(messages.START_TEXT, reply_markup=main_menu_kb)
    else:
        logger.info(f"Пользователь {msg_cbq.from_user.id} вернулся в главное меню через callback='main_menu'")
        msg = await msg_cbq.message.edit_text(messages.RETURN_TO_MAIN_MENU_TEXT, reply_markup=main_menu_kb)
    return msg
