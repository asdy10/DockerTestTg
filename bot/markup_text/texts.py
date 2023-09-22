import datetime
import json

from db.db_connect import Session
from db.queries import DBStore, DBAgent


start_text = 'Выберите какие уведомления хотите настроить\n\n<a href="https://docs.google.com/spreadsheets/d/1elVb3fHKLfna2qm9KK9MaQgIs_REYxUygMSQV41LPbc/edit#gid=0">Ссылка на таблицу "Производство и закупки"</a>'


def format_notice(key, notice, description, dictionary=None, postfix=''):
    if not notice[key]:
        return f'{description}: нет\n'

    if dictionary:
        values = '\n'.join([dictionary[i]['name'] for i in notice[key]])
    else:
        values = '\n'.join(notice[key])

    return f'{description}: {values}{postfix}\n'


def choice_settings_text(doc_name, notice: dict):
    notice = notice[doc_name]
    # 'turn_on': True,
    # 'send_new': True,
    # 'send_updated': False,
    # 'material_store': [], 'article': [], 'days': [],
    # 'text': ['sum', 'plan_quantity', 'produced_quantity', 'articles_text', 'material_store', 'description'],
    # 'positions': ['article', 'size', 'name', 'plan_quantity', 'produced_quantity', 'price']

    with Session.begin() as session:
        stores = DBStore.get_all(session)
        stores = json.loads(str(stores))
        stores_dict = {i['id']: i for i in stores}
        agents = DBAgent.get_all(session)
        agents = json.loads(str(agents))
        agents_dict = {i['id']: i for i in agents}
    s = f'''
Текущие настройки
Уведомления {'✅включены' if notice['turn_on'] else '❌отключены'}
Уведомления о новых {'✅включены' if notice['send_new'] else '❌отключены'}
Уведомления о измененных {'✅включены' if notice['send_updated'] else '❌отключены'}
Показывать {'только проведенные' if notice['applicable'] else 'все'} документы
'''
    if doc_name in ['move', 'supply', 'purchaseorder', 'productiontask']:
        s += format_notice('article', notice, 'Фильтр артикулов')
    if doc_name in ['move', 'supply', 'purchaseorder']:
        s += format_notice('target_store', notice, 'Фильтр на склад', stores_dict)
    if doc_name == 'move':
        s += format_notice('source_store', notice, 'Фильтр со склада', stores_dict)
    if doc_name in ['supply', 'purchaseorder']:
        s += format_notice('agent', notice, 'Фильтр контрагентов', agents_dict)
    if doc_name == 'productiontask':
        s += format_notice('material_store', notice, 'Фильтр фабрик', stores_dict)
    if doc_name in ['purchaseorder', 'productiontask']:
        notice['days'] = [str(i) for i in notice['days']]
        s += format_notice('days', notice, 'Дней до уведомления', postfix=' дней')
    text_settings = {'sum': 'Сумма', 'quantity': 'Общее количество', 'articles_text': 'Артикулы в строчку',
                     'description': 'Комментарий', 'positions': 'Позиции',
                     'source_store': 'Со склада', 'target_store': 'На склад',
                     'agent': 'Контрагент',
                     'produced_quantity': 'Выполнено', 'material_store': 'Цех', }
    s += 'Формат уведомления:\n'
    for text in notice['text']:
        s += f'{text_settings[text]}\n'
    return s
