import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from hendlers import heandlers, admin_heandlers, menu, logs
from DB.database import update_admins


# обработчик завершения скрипта
def signal_handler(sig, frame):
    print("Bot has stoped!")
    sys.exit(0)


# Запуск процесса поллинга новых апдейтов
async def main():

    # получаем токен и создаем объект бота
    with open("token.txt", "r") as token:
        api_token: str = token.read()
    bot = Bot(token=api_token)

    # Диспетчер
    dp = Dispatcher()
    dp.include_router(logs.router)
    dp.include_router(menu.router)
    dp.include_router(admin_heandlers.router)
    dp.include_router(heandlers.router)

    await update_admins()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
