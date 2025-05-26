from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandObject
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any


class ResetStateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data["state"]
        command: CommandObject | None = data.get("command")

        if command:  # Если сообщение содержит команду
            await state.clear()
        res = await handler(event, data)
        return res