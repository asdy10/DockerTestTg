import asyncio
import threading

from aiogram.utils.exceptions import ChatNotFound

#import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, BotCommandScopeChat, ContentType, \
    Message

from healthcheck import health_update, health_check
from scheduler import add_jobs
from data.config import ADMINS
from loader import dp, bot
import filters
import logging

from aiogram.utils.executor import start_webhook


filters.setup(dp)


async def set_commands(dp):
    await dp.bot.set_my_commands(
        commands=[
            BotCommand('start', 'Старт'),
        ]
    )
    commands_for_admin = [
        BotCommand('start', 'Старт'),
    ]
    for admin_id in ADMINS:
        try:
            await dp.bot.set_my_commands(
                commands=commands_for_admin,
                scope=BotCommandScopeChat(admin_id)
            )
        except ChatNotFound as er:
            logging.error(f'Установка команд для администратора {admin_id}: {er}')


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)#, filename='logs.txt'
    logging.info('#####START#####')
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.set_webhook(config.WEBHOOK_URL)
    await set_commands(dp)
    scheduler = add_jobs(bot)
    scheduler.start()
    health_update()
   # await asyncio.create_task(health_check(loop))
    threading.Thread(target=health_check, args=()).start()
    print('run completed')


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


@dp.message_handler(commands='start', state='*')
async def user_menu(message: Message):
    await message.answer('hello')


if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, timeout=250, relax=0.25)
