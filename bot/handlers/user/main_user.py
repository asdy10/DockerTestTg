import datetime
import json

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InputMediaPhoto, ContentType, InputTextMessageContent

# from db.db_connect import Session
# from db.queries import DBUser
from loader import dp, bot
from filters import IsAdmin, IsUser
from markup_text import markups, texts
from states.user_state import NoticeState

from utils.wb_api.official_api import get_cards


@dp.message_handler(IsUser(), commands='start', state='*')
async def user_menu(message: Message, state: FSMContext):
    await state.finish()
    print(message)
    # with Session.begin() as session:
    #     user_id = message.from_user.id
    #     user = DBUser.get(session, user_id)
    #     if not user:
    #         DBUser.add(session, {'user_id': user_id, 'username': message.from_user.username})
    #         user = DBUser.get(session, user_id)
    #     user = json.loads(str(user))
    # async with state.proxy() as data:
    #     data['user'] = user
    await message.answer(texts.start_text, reply_markup=markups.notice_markup(), disable_web_page_preview=True)


@dp.message_handler(IsUser(), commands='remove', state='*')
async def user_menu(message: Message, state: FSMContext):
    await state.finish()
    print(message)
    # with Session.begin() as session:
    #     user_id = message.from_user.id
    #     DBUser.remove(session, user_id)
    await message.answer('Удален')


@dp.callback_query_handler(IsUser(), lambda query: query.data.startswith('choice_seller'), state='*')
async def process_choice_seller(query: CallbackQuery, state: FSMContext):
    seller = SELLERS[int(query.data.split(':')[1])]
    cards = get_cards(seller['api_standart'])
    async with state.proxy() as data:
        data['seller'] = seller
        data['cards'] = cards
        data['cards_id_image'] = {i['vendorCode']: i.get('mediaFiles')[0] if i.get('mediaFiles') != [] else None for i in cards}
    markup = InlineKeyboardMarkup()
    for stock in STOCKS:
        markup.row(InlineKeyboardButton(f'{stock["name"]}', callback_data=f'choice_sklad:{stock["id"]}'))
    # markup.row(InlineKeyboardButton(markups.btn_delete, callback_data=f'wbaccs:delete:{i.wbacc_id}'))
    await query.message.edit_text('Выберите склад', reply_markup=markup)


@dp.callback_query_handler(IsUser(), lambda query: query.data.startswith('choice_sklad'), state='*')
async def process_choice_sklad(query: CallbackQuery, state: FSMContext):
    stock = STOCKS[int(query.data.split(':')[1])]
    async with state.proxy() as data:
        data['stock'] = stock
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Добавить артикулы", switch_inline_query_current_chat=f''))
    await query.message.edit_text('Добавьте артикулы через поиск. Начните вводить артикул и выберите нужный',
                                  reply_markup=markup)


@dp.callback_query_handler(IsUser(), lambda query: query.data.startswith('check_postavka'), state='*')
async def process_check_postavka(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        table_id = data['table_id']
        seller = data['seller']
        choice_articles = data['choice_articles']
        stock = data['stock']
        cards = data['cards']
        cards_id_image = data['cards_id_image']
    args = {'table_id': table_id, 'seller': seller,
            'choice_articles': choice_articles, 'stock': stock,
            'cards': cards, 'cards_id_image': cards_id_image}
    await query.message.delete()
    await query.message.answer('Таблица проверяется...')
    try:
        check_manager_enter(args)
    except Exception as e:
        print('part1', e)
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(f'Проверить', callback_data='check_postavka'))
        await query.message.answer(f'При обработке возникла ошибка, скорее всего указан неверный размер WB, ошибка: {e}. Попробуйте заново', reply_markup=markup)
        #await state.finish()
        return
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(f'Все ок!', callback_data='confirm_postavka:good'),
               InlineKeyboardButton(f'Проверить еще раз', callback_data='check_postavka'))
    markup.row(InlineKeyboardButton(f'Отменить', callback_data='confirm_postavka:cancel'))
    await query.message.answer('Таблица обработана. Проверьте заполнение, особенно колонку "Ошибки", в ней все должно быть ОК', reply_markup=markup)


@dp.callback_query_handler(IsUser(), lambda query: query.data.startswith('confirm_postavka'), state='*')
async def process_check_postavka(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        table_id = data['table_id']
    action = query.data.split(':')[1]
    if action == 'good':
        await query.message.edit_text('Обрабатываю...')
        data = create_move(table_id)
        create_new_lists(table_id, data)
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(f'Обработать таблицу', callback_data=f'make_postavka:{table_id}'))
        #1064154568   383552200
        link = f'https://docs.google.com/spreadsheets/d/{table_id}'
        for i in TO_SEND:
            await bot.send_message(chat_id=i, text=f'Новая поставка! {link}\nЗаполните столбцы H-K(артикул, размер, количество, размер) и после этого нажмите сформировать', reply_markup=markup)
        await state.finish()
        await query.message.edit_text('Поставка создана, ссылка на таблицу отправлена Роману Владимировичу')
    elif action == 'cancel':
        await state.finish()
        await query.message.edit_text('Отменено!')


@dp.callback_query_handler(IsUser(), lambda query: query.data.startswith('make_postavka'), state='*')
async def process_make_postavka(query: CallbackQuery, state: FSMContext):
    table_id = query.data.split(':')[1]

    await query.message.edit_reply_markup(None)
    await query.message.answer('Обрабатывается...')
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(f'Обработать еще раз', callback_data=f'make_postavka:{table_id}'))
    try:
        check_sklad_enter(table_id)
        await query.message.answer('Обработка завершена!', reply_markup=markup)
    except Exception as e:
        await query.message.answer(f'При обработке возникла ошибка. Попробуйте еще раз \n{e}', reply_markup=markup)

