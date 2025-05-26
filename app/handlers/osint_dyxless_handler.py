import logging
import os

from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, InputMediaDocument, FSInputFile

from app.database.requests import Database
from app.texts.callback_datas import OSINT_DYXLESS_CBD
from app.texts.messages import WAIT_TEXT, CHOOSED_DYXLESS, UPDATED_WITH_DYXLESS, ERROR_DYXLESS
from app.utils.dyxless.dyxless import add_info

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == OSINT_DYXLESS_CBD)
async def set_state_for_get_dates(callback: CallbackQuery, db: Database, bot: Bot):
    del_msg = await callback.message.answer(WAIT_TEXT)
    file_id = callback.message.document.file_id
    logger.info(f"Пользователь {callback.from_user.id} выбрал OSINT Dyxless нажав на кнопку с "
                f"callbackdata={OSINT_DYXLESS_CBD}")
    file_name = await add_info(db=db, file_id=file_id, bot=bot)
    await del_msg.delete()

    if file_name is None:
        await callback.message.edit_reply_markup(None)
        res = await callback.message.answer(ERROR_DYXLESS)
        logger.info(f'Ошибка получения данных с dyxless')
    else:
        file = FSInputFile(file_name)
        res = await callback.message.edit_media(
            media=InputMediaDocument(media=file, caption=UPDATED_WITH_DYXLESS),
            reply_markup=None
        )
        if os.path.exists(file_name):
            os.remove(file_name)
        logger.info(f'Пользователю {callback.message.from_user.id} отправлен файл с OSINT dyxless')
    return res
