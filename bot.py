from database import init_db
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я помогу вам делиться лучшими фильмами, книгами, треками и местами. Напишите /help, чтобы узнать больше!")


async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
