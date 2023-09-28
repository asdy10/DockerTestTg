import asyncio
import datetime
import json
import random
import threading
import time

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.healthcheck import health_update

#from db.db_buffer import db_buffer
#from db.db_connect import Session
#from db.queries import DBUser, DBProductionTask, DBMove, DBSupply, DBPurchaseOrder
#from markup_text import texts, markups

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def task_update_db_send_notices_new_updated(bot: Bot):
    to_update = ['product', 'variant', 'store', 'counterparty']
    for i in to_update:
        update_add_all_items(i, 10)
    db_buffer.update_from_db()
    documents = get_edited_documents(10)
    new, updated = update_edited_documents_return_new_updated(documents)
    with Session.begin() as session:
        users = DBUser.get_all(session)
        users = json.loads(str(users))
    db_classes = {'productiontask': DBProductionTask, 'move': DBMove,
                  'purchaseorder': DBPurchaseOrder, 'supply': DBSupply}
    docs = [{'name': 'new', 'doc': new, 'text': '<b>НОВЫЙ документ</b>\n'},
            {'name': 'updated', 'doc': updated, 'text': '<b>ИЗМЕНЕННЫЙ документ</b>\n'}]
    for doc_type in docs:
        for doc in doc_type['doc']:
            print(doc_type['name'], doc)
            document_id = doc['document_id']
            doc_name = doc['name']
            with Session.begin() as session:
                document = db_classes[doc_name].get(session, document_id)
                document = json.loads(str(document))
            for user in users:
                print(user['notice'][doc_name])
                args = {'document': document, 'doc_name': doc_name,
                        'notice': user['notice'][doc_name], 'doc_type_name': doc_type['name']}
                if filter_notice(args):
                    continue
                need_add_positions = 'positions' in user['notice'][doc_name]['text']
                text_format = user['notice'][doc_name]['text']
                text = doc_type['text']

                text_settings = {'amount': 'Сумма', 'applicable': 'Проведено', 'name': 'Название',
                                 'description': 'Комментарий',
                                 'agent_id': 'Контрагент', 'target_store_id': 'На склад',
                                 'positions': 'Позиции', 'state': 'Статус', 'purchase_order_id': 'Связанный заказ поставщика',
                                 'delivery_planned': 'Плановая дата поставки', 'source_store_id': 'Со склада',
                                 'production_start': 'Старт производства', 'materials_store_id': 'Склад материалов(цех)',
                                 'products_store_id': 'Склад поставки(цех)',
                                 }
                if document['edited'] not in [[], None]:
                    text += 'Изменено: '
                    text += ', '.join([text_settings[i] for i in document['edited']])
                    text += '\n'

                document['doc_type'] = doc_name
                text += transform_document_to_text(document, need_add_positions, text_format)
                try:
                    await bot.send_message(chat_id=user['user_id'], text=text)
                except:
                    pass


def filter_notice(args):
    document = args['document']
    doc_name = args['doc_name']
    notice = args['notice']
    doc_type_name = args.get('doc_type_name')
    day = args.get('day')
    if not notice['turn_on']:
        return True
    if doc_type_name:
        if not notice[f'send_{doc_type_name}']:
            return True
    if notice['applicable']:
        if not document['applicable']:
            return True
    if doc_name in ['purchaseorder', 'productiontask']:
        if day:
            if day not in notice['days']:
                return True
    if doc_name in ['move', 'supply', 'purchaseorder', 'productiontask']:
        if notice['article'] != []:
            for pos in document['positions']:
                product = None
                if pos['type'] == 'product':
                    product = db_buffer.get_product(pos['id'])
                elif pos['type'] == 'variant':
                    variant = db_buffer.get_variant(pos['id'])
                    product = db_buffer.get_product(variant['product'])
                if product:
                    if product['article'] in notice['article']:
                        return False
            return True
    if doc_name in ['move', 'supply', 'purchaseorder']:
        if notice['target_store'] != []:
            if document['target_store_id'] in notice['target_store']:
                return False
            else:
                return True
    if doc_name == 'move':
        if notice['source_store'] != []:
            if document['source_store_id'] in notice['source_store']:
                return False
            else:
                return True
    if doc_name in ['supply', 'purchaseorder']:
        if notice['agent'] != []:
            if document['agent_id'] in notice['agent']:
                return False
            else:
                return True
    if doc_name == 'productiontask':
        if notice['material_store'] != []:
            if document['materials_store_id'] in notice['material_store']:
                return False
            else:
                return True
    return False


async def task_update_table_send_notices_by_calendar(bot: Bot):
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now() + datetime.timedelta(days=60)
    all_documents = get_documents_from_db(start_date, end_date)
    calendar1, calendar2 = get_calendars_by_db_data(all_documents, start_date, end_date)
    table1 = create_table_from_calendar(calendar1)
    table2 = create_table_from_calendar(calendar2)
    table_id = TABLE_ID
    ranges1 = f'Календарь!A2:H1000'
    ranges2 = f'Полная информация!A2:H1000'
    add_colors(table1)
    update_table(table_id, table1, ranges1)
    clear_table(table_id, ranges1)
    update_table(table_id, table1, ranges1)
    clear_table(table_id, ranges2)
    update_table(table_id, table2, ranges2)
    await send_notices_by_calendar(bot, calendar1)


async def send_notices_by_calendar(bot: Bot, calendar):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    result = []
    for week in calendar:
        for d, item in week.items():
            if item:
                if item['date'] > date:
                    result.append(item['all'])
    for i in result:
        print(i)
    with Session.begin() as session:
        users = DBUser.get_all(session)
        users = json.loads(str(users))
    for day, item in enumerate(result):
        if item:
            for document in item:
                doc_name = document['doc_type']
                if doc_name in ['move', 'supply']:
                    continue
                for user in users:
                    args = {'document': document, 'doc_name': doc_name,
                            'notice': user['notice'][doc_name], 'day': day}
                    if filter_notice(args):
                        continue
                    need_add_positions = 'positions' in user['notice'][doc_name]['text']
                    text_format = user['notice'][doc_name]['text']
                    text = f'Через {day} дней планируется поставка\n' if day != 0 else 'Завтра планируется поставка\n'

                    text += transform_document_to_text(document, need_add_positions, text_format)
                    try:
                        await bot.send_message(chat_id=user['user_id'], text=text)
                    except:
                        pass


async def task_test():
    print('start')
    loop = asyncio.get_event_loop()
    now = loop.time()
    try:
        async with asyncio.timeout(5):
            print('start2')
            await test_def()
    except TimeoutError:
        print('wtf')


async def test_def():
    print('start3')
    t = random.randint(1, 15)
    print('time', t)
    for i in range(t):
        print('hello', i)
        time.sleep(1)
    time.sleep(100)
    health_update()


def add_jobs(bot):
    scheduler.add_job(test_def, "interval", seconds=10, args=[], misfire_grace_time=None, coalesce=True)
    #scheduler.add_job(task_send_questions, "interval", seconds=600, args=[bot], misfire_grace_time=None, coalesce=True)
    #scheduler.add_job(task_update_table_send_notices_by_calendar, 'cron', hour=12, args=[bot])
    return scheduler

