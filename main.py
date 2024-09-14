import asyncio
import os
from dotenv import find_dotenv, load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from handlers import game_hanlers


load_dotenv(find_dotenv())


async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)

    dp.include_router(game_hanlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([types.BotCommand(command='game', description='Игра 21')], scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())