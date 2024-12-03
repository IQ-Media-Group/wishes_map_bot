import asyncio
import logging

from aiogram import Bot, Dispatcher

from core.db.scripts import get_user
from core.routers.main_router import router as main_router
from core.routers.register import router as register_router
from core.routers.wish_days import router as wish_router, send_daily_msgs
from core.db.config import settings


def register_messages(dp: Dispatcher):
    """
    Routers registration
    :param dp:
    """
    dp.include_router(wish_router)
    dp.include_router(register_router)
    dp.include_router(main_router)


async def start():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(settings.TOKEN)
    dp = Dispatcher()

    register_messages(dp=dp)

    asyncio.create_task(send_daily_msgs(bot))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
    ...
