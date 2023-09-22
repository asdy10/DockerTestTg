import asyncio
import os
import threading
import time

from aiogram.utils.exceptions import ChatNotFound

import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, BotCommandScopeChat, ContentType, \
    Message

from data import config
from data.config import ADMINS
from loader import dp, bot
import filters
import logging

#from scheduler import add_jobs, task_update_db_send_notices_new_updated, task_update_table_send_notices_by_calendar

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


@dp.message_handler(content_types=ContentType.PHOTO)
async def process_review_photo(message: Message):
    print('wtf')
    fileID = message.photo[-1].file_id
    print(message.caption)
    print(fileID)


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)  # , filename='logs.txt'
    logging.info('#####START#####')
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(dp)
    #await asyncio.create_task(task_update_db_send_notices_new_updated(bot))
    # await asyncio.create_task(task_update_table_send_notices_by_calendar(bot))
    print('run completed')


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, timeout=250, relax=0.25)
