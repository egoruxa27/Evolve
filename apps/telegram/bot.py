from os import getenv
import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Hello, {message.from_user.full_name}, твой id {message.from_user.id}!")

#Добавить регитсрацию пользователя для построения связи в бд.
@dp.message(Command('register'))
async def register(message: Message):
    await message.answer(f'Ведите код подтверждения полученный на сайте.')

@dp.message(Command('help'))
async def help_command(message: Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/start — начать работу\n"
        "/register — регистрация"
    )

@dp.message(Command("get_task"))
async def get_task(message: Message):
    await message.answer('Список ваших задач.')

@dp.message()
async def unknown(message: Message) -> None:
    if message.text and message.text.startswith('/'):
        await message.answer(
            'Неизвестная команда. Список команд можно посмотреть: /help'
        )

async def main():
    bot = Bot(token=getenv('BOT_TOKEN'))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())