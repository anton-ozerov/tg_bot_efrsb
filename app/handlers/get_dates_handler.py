import logging
import os
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

from app.database.requests import Database
from app.keyboards.back_to_main_menu_kb import back_main_menu_kb
from app.keyboards.choose_osint_kb import choose_osint_ikb
from app.states.get_dates_st import GetDates
from app.texts.buttons import ERROR_INPUTTING_DATES
from app.texts.callback_datas import GET_DATES_CBD
from app.texts.messages import INPUT_DATES_RANGE_TEXT, WAIT_TEXT, CHOOSE_OSNIT_TEXT
from app.utils.efrsb.parse_data import get_objects_in_date_range

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == GET_DATES_CBD)
async def set_state_for_get_dates(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(INPUT_DATES_RANGE_TEXT, reply_markup=back_main_menu_kb)
    await state.set_state(GetDates.dates_1_2)
    logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку с callbackdata={GET_DATES_CBD} - "
                f"Установился state для ввода даты")


@router.message(GetDates.dates_1_2)  # для состояния ввода имени
async def get_dates(message: Message, state: FSMContext, db: Database):
    del_msg = await message.answer(WAIT_TEXT)

    dates_range = message.text.split('-')

    try:
        if len(dates_range) != 2:
            raise ValueError
        date1 = datetime.strptime(dates_range[0], '%Y.%m.%d')
        date2 = datetime.strptime(dates_range[1], '%Y.%m.%d')
        if date1 > date2:
            raise ValueError
    except ValueError as e:
        await del_msg.delete()
        logger.error(f'Неверный формат ввода даты у пользователя {message.from_user.id}. Ошибка {e}. Попытка ввода ещё раз')
        return await message.answer(ERROR_INPUTTING_DATES, reply_markup=back_main_menu_kb)

    await state.clear()
    file_name = await get_objects_in_date_range(date_1=date1, date_2=date2, db=db)
    await del_msg.delete()
    file = FSInputFile(file_name)
    res = await message.answer_document(document=file, caption=CHOOSE_OSNIT_TEXT, reply_markup=choose_osint_ikb)
    if os.path.exists(file_name):
        os.remove(file_name)
    logger.info(f'Пользователю {message.from_user.id} отправлен файл {file_name} в промежутке дат {str(date1)} - {str(date2)}')
    return res
