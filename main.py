import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.data.config import BOT_TOKEN, LOG_FILE, DB_NAME
from app.database.base import Base
from app.handlers import main_menu, get_dates_handler, osint_dyxless_handler
from app.middlewares.db import DatabaseMiddleware
from app.middlewares.delete_old_reply_markup import RemoveReplyMarkupMiddleware
from app.middlewares.reset_states_to_commands import ResetStateMiddleware


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                        handlers=[
                            RotatingFileHandler(
                                filename=LOG_FILE,
                                maxBytes=5 * 1024 * 1024,  # 5 MB
                                backupCount=3,
                                encoding="utf-8"
                            ),
                            logging.StreamHandler()
                        ])

    engine = create_async_engine(url=f'sqlite+aiosqlite:///{DB_NAME}')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = async_sessionmaker(engine)

    dp.update.middleware(DatabaseMiddleware(session=session))  # для БД
    dp.update.middleware(ResetStateMiddleware())  # удаление состояний при вводе команд
    dp.update.middleware(RemoveReplyMarkupMiddleware())  # удаление инлайн клавиатур у Message при новом Message

    dp.include_routers(main_menu.router, get_dates_handler.router, osint_dyxless_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('EXIT')