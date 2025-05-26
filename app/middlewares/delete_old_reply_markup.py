import logging
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram import Bot
from aiogram.types import Message, TelegramObject


logger = logging.getLogger(__name__)


class RemoveReplyMarkupMiddleware(BaseMiddleware):
    """Удаление inline кнопок у старых Message'ей"""
    def __init__(self):
        self.last_bot_messages: dict[int, list[int]] = {}  # Хранение последних сообщений {user_id: message_id}
        self.last_media_group_id: dict[int, list[int]] = {}  # Хранение последних id медиагруппы {user_id: media_group_id}

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]

        if event.message:  # Если пользователь отправляет Message
            user_id = event.message.from_user.id

            # Удаляем клавиатуру у предыдущих сообщений, если они есть
            if user_id in self.last_bot_messages:
                self.last_bot_messages[user_id].extend([event.message.message_id - i for i in range(1, 21)])
                for message_id in self.last_bot_messages[user_id]:
                    try:
                        await bot.edit_message_reply_markup(
                            chat_id=user_id,
                            message_id=message_id,
                            reply_markup=None
                        )
                        logger.debug(f'Удалили reply_markup у сообщения {message_id} для пользователя {user_id}')
                    except Exception as e:
                        pass

            self.last_bot_messages[user_id] = []  # очищаем список еще до result

            # Сохраняем ID нового сообщения
            result = await handler(event, data)
            try:
                self.last_bot_messages[result.chat.id].append(result.message_id)
            except AttributeError:  # когда UNHANDLED
                pass

            return result
        return await handler(event, data)
