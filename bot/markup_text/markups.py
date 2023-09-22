from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

btn_confirm = '✅ Подтвердить'
btn_all_right = '✅ Все верно'
btn_cancel = '🚫 Отменить'
btn_change = '✍️  Изменить'
btn_ready = '✅  Готово'
btn_back = '👈 Назад'

btn_add_balance = 'Пополнить баланс'
btn_make_payment = '💳 Оплатить'
btn_link_for_payment = '🔗 Ссылка на оплату'

btn_delete = 'Удалить'
btn_add_new = 'Добавить новый'

btn_answer = 'Ответить'
btn_discard = 'Отклонить'


def notice_markup():
    markup = InlineKeyboardMarkup()
    notices_names = {'move': 'Перемещение', 'supply': 'Приемка',
                    'purchaseorder': 'Заказ поставщика', 'productiontask': 'Производственное задание',
                    #'other': 'Другое'
                     }
    for doc, name in notices_names.items():
        markup.row(InlineKeyboardButton(name, callback_data=f'notice_doc:{doc}'))

    return markup


def doc_markup(name, notice):
    button_mappings = {
        'move': [('Артикул', 'article'), ('На склад', 'target_store'), ('Со склада', 'source_store'), ('Текст уведомления', 'text')],
        'supply': [('Артикул', 'article'), ('На склад', 'target_store'), ('Контрагент', 'agent'), ('Текст уведомления', 'text')],
        'purchaseorder': [('Артикул', 'article'), ('На склад', 'target_store'), ('Контрагент', 'agent'), ('Дней до уведомления', 'days'), ('Текст уведомления', 'text')],
        'productiontask': [('Артикул', 'article'), ('Дней до уведомления', 'days'), ('Фабрика', 'material_store'), ('Текст уведомления', 'text')],
        'other': [('Заканчивается товар', 'out_stock'), ('лежит на складе более...', 'oborot')]
    }

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton('Отключить все' if notice[name]['turn_on'] else 'Включить все', callback_data=f'notice_filters:turn_on'))
    markup.row(InlineKeyboardButton('Отключить новые' if notice[name]['send_new'] else 'Включить новые', callback_data=f'notice_filters:send_new'))
    markup.row(InlineKeyboardButton('Отключить измененные' if notice[name]['send_updated'] else 'Включить измененные', callback_data=f'notice_filters:send_updated'))
    markup.row(InlineKeyboardButton('Показывать и не проведенные' if notice[name]['applicable'] else 'Только проведенные', callback_data=f'notice_filters:applicable'))

    for text, data in button_mappings.get(name, []):
        markup.row(InlineKeyboardButton(text, callback_data=f'notice_filters:{data}'))
    markup.row(InlineKeyboardButton(btn_back, callback_data=f'notice_filters:back'))
    return markup


def store_markup(stores, choice):
    markup = InlineKeyboardMarkup()
    for store in stores:
        s = '✅ ' if store['id'] in choice else ''
        markup.row(InlineKeyboardButton(s + store['name'], callback_data=f'notice_filter_store:{store["id"]}'))
    markup.row(InlineKeyboardButton(btn_ready, callback_data=f'notice_filter_store:confirm'))
    return markup


def days_markup(choice):
    markup = InlineKeyboardMarkup()
    days = [0, 3, 7, 14]
    for day in days:
        s = '✅ ' if day in choice else ''
        markup.row(InlineKeyboardButton(f'{s} {day} дней', callback_data=f'notice_filter_days:{day}'))
    markup.row(InlineKeyboardButton(btn_ready, callback_data=f'notice_filter_days:confirm'))
    return markup


def text_settings_markup(choice, doc_name):
    text_settings = {'sum': 'Сумма', 'quantity': 'Общее количество', 'articles_text': 'Артикулы в строчку',
                     'description': 'Комментарий',
                     'positions': 'Позиции'}
    if doc_name == 'move':
        text_settings = text_settings | {'source_store': 'Со склада', 'target_store': 'На склад', }
    elif doc_name in ['supply', 'purchaseorder']:
        text_settings = text_settings | {'agent': 'Контрагент', 'target_store': 'На склад', }
    elif doc_name == 'productiontask':
        text_settings = text_settings | {'produced_quantity': 'Выполнено', 'material_store': 'Цех', }
    markup = InlineKeyboardMarkup()
    for t in text_settings:
        s = '✅ ' if t in choice else ''
        markup.row(InlineKeyboardButton(f'{s} {text_settings[t]}', callback_data=f'notice_text:{t}'))
    markup.row(InlineKeyboardButton(btn_ready, callback_data=f'notice_text:confirm'))
    return markup
