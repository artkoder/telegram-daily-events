import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers.start import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token="TEST:TOKEN", default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
