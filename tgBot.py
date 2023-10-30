from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.utils.exceptions import UserDeactivated, ChatNotFound, RetryAfter, BotBlocked
from collections import Counter
import random
import sqlite3
import shelve
from datetime import datetime as dt
import time
import asyncio
import threading

card_for_promo = -1
chosen_card = -1
medals = ['🥇', '🥈', '🥉']
colors = ['⚪️', '🔵', '🟣', '🟡', 'реальная вещь']
pass_times = ['1 день', '1 неделя', '1 месяц']
CHANNEL_ID = '-1001938709594'
CHANNEL_ID1 = '-1001772643909'
dp = Dispatcher(bot)
notsub_message = '❗️Чтобы сыграть, подпишитесь на наш канал <b>To Bless</b>, а также на наших друзей из <b>DANISA SHOP</b> ⬇️'
#notsub_message = '❗️Чтобы сыграть, подпишитесь на наш канал ⬇️'
pack_cards = {}


async def add_referal(message, referer_id):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT refs, free, level, cur_level FROM users WHERE user_id = {referer_id}')
    data1 = cur.fetchone()
    data = list(data1)
    data[0] += 1
    if data[1] < 400:
        data[3] += 1
        if data[2] == data[3]:
            data[1] += 1
            data[3] = 0
        if data[1] % 50 == 0 and data[2] > 1 and data[1] != 0:
            data[2] -= 1
    #await bot.send_message(referer_id, f'{data}')
    cur.execute(f'UPDATE users SET refs = {data[0]}, free = {data[1]}, level = {data[2]}, cur_level = {data[3]} WHERE user_id = {referer_id}')
    con.commit()
    cur.execute(f'SELECT username, f_name, l_name FROM users WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data[2] != None:
        name = data[1] + ' ' + data[2]
    else:
        name = data[1]
    await bot.send_message(referer_id,
                           f'🍾 Поздравляем, пользователь <b>{name}</b> (@{data[0]}) только что начал играть в ToBless Cartoon по твоей ссылке!',
                           parse_mode='html')
    cur.close()
    con.close()


async def check_update():
    while True:
        await asyncio.sleep(1)
        today = dt.now()
        if today.minute % 30 == 0 and today.second == 0:
            await bot.send_message(732620293,
                                   'gdgd')

async def season_update():
    global medals
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    while True:
        await asyncio.sleep(1)
        today = dt.now()
        if today.day == 1 and today.hour == 0 and today.minute == 0 and today.second == 1:
            cur.execute('SELECT username, season_score FROM users ORDER BY season_score DESC LIMIT 10')
            data = cur.fetchall()
            output = '❗️ Топ-10 игроков <b>в конце этого сезона</b>\n\n'
            for i in range(len(data)):
                if i <= 2:
                    output += medals[i]
                else:
                    output += str(i + 1)
                    output += '.'
                output += f'@{data[i][0]} (Score: <b>{data[i][1]}</b>)\n'
            await bot.send_message(429229342, output, parse_mode='html')
            cur.execute(f'UPDATE users SET season_score = 0')
            con.commit()
    cur.close()
    con.close()

async def push_update():
    con1 = sqlite3.connect('tobless.sql')
    cur1 = con1.cursor()
    diff = 3 * 3600
    a = 0
    while True:
        await asyncio.sleep(1)
        t = time.time()
        cur1.execute(f'SELECT user_id, timer FROM users WHERE push = 1')
        data = cur1.fetchall()
        if data != None:
            for el in data:
                if (t - el[1]) >= diff:
                    #await bot.send_message(732620293, f'{el[0]}')
                    try:
                        #await bot.send_message(732620293, f'{el[0]}')
                        await bot.send_message(el[0], '⏰ Бро, у тебя снова появилась возможность получить новую карточку! Воспользуйся ей скорее!')
                    except UserDeactivated:
                        a = 1
                    except ChatNotFound:
                        a = 2
                    except BotBlocked:
                        a = 3
                    cur1.execute(f'UPDATE users SET push = 0 WHERE user_id = {el[0]}')
                    con1.commit()
    cur1.close()
    con1.close()

async def alert_update():
    con3 = sqlite3.connect('tobless.sql')
    cur3 = con3.cursor()
    a = 0
    while True:
        await asyncio.sleep(1)
        t = time.time()
        cur3.execute(f'SELECT user_id FROM users WHERE alert = 1')
        data = cur3.fetchall()
        if data != None:
            for el in data:
                try:
                    '''media = types.MediaGroup()
                    media.attach_photo(types.InputFile('halloween/hall1.jpg'),
                                       'Начался новый ивент, успей выбить лимитированные карты!')
                    for i in range(2, 9):
                        filename = f'halloween/hall{i}.jpg'
                        media.attach_photo(types.InputFile(filename))
                    await bot.send_media_group(chat_id = el[0], media = media)'''
                    file = open('./tara.jpg', 'rb')
                    await bot.send_photo(el[0], file,
                                         f'В канале уже запущен розыгрыш на такую футболку, успей принять участие!')
                except UserDeactivated:
                    a = 1
                except ChatNotFound:
                    a = 2
                except BotBlocked:
                    a = 3
                cur3.execute(f'UPDATE users SET alert = 0 WHERE user_id = {el[0]}')
                con3.commit()
    cur3.close()
    con3.close()

async def pass_update():
    con2 = sqlite3.connect('tobless.sql')
    cur2 = con2.cursor()
    diff = [86400, 604800, 2592000]
    while True:
        await asyncio.sleep(1)
        t = time.time()
        cur2.execute(f'SELECT user_id, pass_time, pass_status FROM users WHERE pay_pass = 1')
        data = cur2.fetchall()
        if data != None:
            for el in data:
                if (t - el[1]) >= diff[el[2] - 1]:
                    cur2.execute(f'UPDATE users SET pay_pass = 0, pass_time = 0, push = 0, pass_status = 0 WHERE user_id = {el[0]}')
                    con2.commit()
                    await bot.send_message(el[0], '❗️ Твоя подписка Pay Pass закончилась')
    cur2.close()
    con2.close()

def check_sub_channel(chat_member):
    if chat_member['status'] != 'left':
        return True
    else:
        return False

async def create_sql():
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT UNIQUE NOT NULL,
            username VARCHAR,
            f_name VARCHAR,
            l_name VARCHAR,
            pay_pass BOOLEAN,
            pass_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            push INT DEFAULT 0,
            get_cards_times INT DEFAULT 0,
            total_score INT DEFAULT 0,
            season_score INT DEFAULT 0,
            clan_id INT DEFAULT 0,
            timer  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            refs INT DEFAULT 0,
            free INT DEFAULT 0,
            level INT DEFAULT 5,
            cur_level INT DEFAULT 0,
            pass_status INT,
            alert INT
        )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS cards(
            id BIGINT UNIQUE NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR, 
            rarity INT NOT NULL,
            score INT NOT NULL,
            path_to VARCHAR NOT NULL UNIQUE,
            pass_rarity INT
        )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS drop_cards(
                id BIGINT UNIQUE NOT NULL,
                title VARCHAR NOT NULL,
                description VARCHAR, 
                rarity INT NOT NULL,
                score INT NOT NULL,
                path_to VARCHAR NOT NULL UNIQUE,
                pass_rarity INT
            )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS users_cards(
            user_id BIGINT NOT NULL,
            card_id BIGINT NOT NULL,
            FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS users_cards1(
                user_id BIGINT,
                card_id BIGINT,
                kolvo BIGINT,
                rarity INT
            )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS users_iterations(
            user_id BIGINT UNIQUE,
            current_card INT,
            cards INT[],
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS bild_infos(
            user_id BIGINT NOT NULL,
            bild_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS promos(
                id BIGINT UNIQUE NOT NULL,
                card_id BIGINT NOT NULL,
                promo VARCHAR,
                times BIGINT
            )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS users_promos(
                    user_id BIGINT NOT NULL,
                    promo VARCHAR
                )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS banned(
                    user_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR,
                    ban_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
    con.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS refers(
                        referal_id BIGINT UNIQUE NOT NULL,
                        referer_id BIGINT,
                        commited INT
                    )""")
    con.commit()

    cur.close()
    con.close()

async def register_user(message: types.Message):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    #people_id = message.from_user.id
    '''cur.execute(f"SELECT user_id FROM users WHERE user_id = {people_id}")
    data = cur.fetchone()
    if data is None:'''
    us_id = message.from_user.id
    name = message.from_user.username
    first = message.from_user.first_name
    last = message.from_user.last_name
    cur.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 1)", (us_id, name, first, last))
    con.commit()

    '''cur.execute("SELECT title, description, score, path_to FROM cards WHERE id = 1")
    data = cur.fetchone()
    bot.send_message(message.chat.id, str(data))
    title, des, sc, path = data
    file = open('./'+path, 'rb')
    bot.send_photo(message.chat.id, file,f'{title}\n\n{des}\n\nЦена: {sc}')'''
    cur.close()
    con.close()

async def delete():
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute("DELETE FROM users")
    con.commit()
    cur.close()
    con.close()

'''def on_click(message):
    if message.text == 'Получить карту':
        if check_sub_channel(bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id).status):
            bot.send_message(message.chat.id, 'получай карту!')
        else:
            bot.send_message(message.from_user.id, notsub_message, reply_markup=checksub)
    bot.register_next_step_handler(message, on_click)'''

checksub = types.InlineKeyboardMarkup()
btnUrlChannel = types.InlineKeyboardButton('TO BLESS', url = 'https://t.me/tobles2')
btnUrlChannel1 = types.InlineKeyboardButton('DANISA SHOP', url = 'https://t.me/DANISA_SHOP')
checksub.row(btnUrlChannel, btnUrlChannel1)
#checksub.row(btnUrlChannel1)

basicMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btnGetCard = types.KeyboardButton('🃏 Получить карту')
btnMyCards = types.KeyboardButton('🌮 Мои карты')
btnMenu = types.KeyboardButton('Ⓜ️ Меню')
basicMarkup.row(btnGetCard, btnMyCards)
basicMarkup.row(btnMenu)

adminMarkup = types.InlineKeyboardMarkup()
btnAddCard = types.InlineKeyboardButton('Добавить карту', callback_data='add_card')
btnDelCard = types.InlineKeyboardButton('Удалить карту', callback_data='del_card')
btnAddPromo = types.InlineKeyboardButton('Добавить промокод', callback_data='add_promo')
btnShowPromos = types.InlineKeyboardButton('Показать промокоды', callback_data='show_promos')
btnUsersInfo = types.InlineKeyboardButton('Инфа об игроках', callback_data='users_info')
adminMarkup.row(btnAddCard, btnDelCard)
adminMarkup.row(btnAddPromo, btnShowPromos)
adminMarkup.row(btnUsersInfo)

addedCardMarkup = types.InlineKeyboardMarkup()
btnOk = types.InlineKeyboardButton('Все верно!', callback_data='right_card')
btnChange = types.InlineKeyboardButton('Изменить', callback_data='change_card')
addedCardMarkup.row(btnOk, btnChange)

addedPassCardMarkup = types.InlineKeyboardMarkup()
btnPassOk = types.InlineKeyboardButton('Все верно!', callback_data='right_card')
btnPassChange = types.InlineKeyboardButton('Изменить', callback_data='change_pass_card')
addedPassCardMarkup.row(btnPassOk, btnPassChange)

changeCardMarkup = types.InlineKeyboardMarkup()
btnChangePhoto = types.InlineKeyboardButton('Фото', callback_data='change_photo')
btnChangeName = types.InlineKeyboardButton('Название', callback_data='change_name')
btnChangeDesc = types.InlineKeyboardButton('Описание', callback_data='change_desc')
btnChangeRar = types.InlineKeyboardButton('Редкость', callback_data='change_rar')
btnChangePrice = types.InlineKeyboardButton('Стоимость', callback_data='change_price')
changeCardMarkup.row(btnChangePhoto, btnChangeName)
changeCardMarkup.row(btnChangeDesc, btnChangeRar)
changeCardMarkup.row(btnChangePrice)

changePassCardMarkup = types.InlineKeyboardMarkup()
btnChangePassPhoto = types.InlineKeyboardButton('Фото', callback_data='change_photo')
btnChangePassName = types.InlineKeyboardButton('Название', callback_data='change_name')
btnChangePassDesc = types.InlineKeyboardButton('Описание', callback_data='change_desc')
btnChangePassRar = types.InlineKeyboardButton('Длительность Pass', callback_data='change_pass_rar')
changePassCardMarkup.row(btnChangePassPhoto, btnChangePassName)
changePassCardMarkup.row(btnChangePassDesc, btnChangePassRar)

acceptDelMarkup = types.InlineKeyboardMarkup()
btnBack = types.InlineKeyboardButton('Выбрать другую', callback_data='del_card')
btnAcceptDel = types.InlineKeyboardButton('Удалить', callback_data = 'accept_del')
acceptDelMarkup.row(btnBack, btnAcceptDel)

btnRight = types.InlineKeyboardButton('➡️', callback_data='move_right')
btnLeft = types.InlineKeyboardButton('⬅️', callback_data='move_left')
btnBack = types.InlineKeyboardButton('↩️ Вернуться', callback_data='move_back')

menuMarkup = types.InlineKeyboardMarkup(row_width=1)
btnPass = types.InlineKeyboardButton('💲 Pay Pass', callback_data='pay_pass')
btnPromo = types.InlineKeyboardButton('☄️ Промокод', callback_data='use_promo')
btnTop = types.InlineKeyboardButton('🏆 Top', callback_data='choose_top')
btnRef = types.InlineKeyboardButton('🫂 Реферальная программа', callback_data='my_ref')
btnRules = types.InlineKeyboardButton('📕 Правила', callback_data='rules')
btnCraft = types.InlineKeyboardButton('🛠 Крафт', callback_data='craft')
menuMarkup.add(btnRules, btnCraft, btnPass, btnPromo, btnTop, btnRef)

btnMenuBack = types.InlineKeyboardButton('↩️ Вернуться', callback_data='menu_back')

acceptAddPromoMarkup = types.InlineKeyboardMarkup()
btnBackPromo = types.InlineKeyboardButton('Выбрать другую', callback_data='add_promo')
btnAcceptPromo = types.InlineKeyboardButton('Все верно', callback_data = 'accept_promo')
acceptAddPromoMarkup.row(btnBackPromo, btnAcceptPromo)

topMarkup = types.InlineKeyboardMarkup(row_width=1)
btnTopSeason = types.InlineKeyboardButton('💥 Топ 10 в этом сезоне', callback_data='top_season')
btnTopAll = types.InlineKeyboardButton('🌟 Топ 10 за все время', callback_data='top_all')
btnTopClans = types.InlineKeyboardButton('🏆 Топ кланов', callback_data='top_clans')
topMarkup.add(btnTopSeason, btnTopAll, btnTopClans)

chooseCardTypeMarkup = types.InlineKeyboardMarkup()
btnDefCard = types.InlineKeyboardButton('Дефолт карта', callback_data='default_card')
btnPassCard = types.InlineKeyboardButton('Pass карта', callback_data='pass_card')
chooseCardTypeMarkup.row(btnDefCard, btnPassCard)

craftMarkup = types.InlineKeyboardMarkup(row_width=1)
btnCraftWhite = types.InlineKeyboardButton('Скрафтить из 10 ⚪️', callback_data='craft_white')
btnCraftBlue = types.InlineKeyboardButton('Скрафтить из 10 🔵', callback_data='craft_blue')
btnCraftPurple = types.InlineKeyboardButton('Скрафтить из 10 🟣', callback_data='craft_purple')
craftMarkup.add(btnCraftWhite, btnCraftBlue, btnCraftPurple)


async def print_added_card(message: types.Message):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute('SELECT * FROM cards ORDER BY id DESC LIMIT 1')
    data = cur.fetchone()
    await bot.send_message(message.chat.id, 'Новая карточка готова, вот она!')
    file = open('./' + data[5], 'rb')
    if data[4] != 0:
        await bot.send_photo(message.chat.id, file,
                             f'🥡Держи бро, вот твоя карта!\n<b>{data[1]}</b>\n<i>{data[2]}</i>\nScore: <b>{data[4]}</b>',
                             parse_mode='html', reply_markup=addedCardMarkup)
    else:
        await bot.send_photo(message.chat.id, file,
                             f'🥡Держи бро, вот твоя карта!\n<b>{data[1]}</b>\n<i>{data[2]}</i>',
                             parse_mode='html', reply_markup=addedPassCardMarkup)


async def show_cards(message: types.Message):
    global pack_cards, btnRight, btnLeft, btnBack
    showCardsMarkup = types.InlineKeyboardMarkup()
    cur_card = pack_cards[message.chat.id]
    current = cur_card[1]
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM cards WHERE id = {cur_card[current+3][0]}')
    data = cur.fetchone()
    cur.execute(f'SELECT season_score FROM users WHERE user_id = {message.chat.id}')
    data1 = cur.fetchone()
    if cur_card[0] == 1:
        btnCurrentCard = types.InlineKeyboardButton(f'({current+1}/{pack_cards[message.chat.id][0]})', callback_data='nothing')
        showCardsMarkup.row(btnCurrentCard)
        showCardsMarkup.row(btnBack)
        file = open('./' + data[5], 'rb')
        await bot.send_photo(message.chat.id, file,
                       f'<b>{data[1]}</b>\n<i>{data[2]}</i>\nЦена карточки: <b>{data[4]}</b>\n\nКоличество: <b>{cur_card[current+3][1]}</b>\nScore в этом сезоне: <b>{data1[0]}</b>',
                       parse_mode='html', reply_markup = showCardsMarkup)
    else:
        if cur_card[1] == 0:
            btnCurrentCard = types.InlineKeyboardButton(f'({current+1}/{pack_cards[message.chat.id][0]})', callback_data='nothing')
            showCardsMarkup.row(btnCurrentCard, btnRight)
            showCardsMarkup.row(btnBack)
            file = open('./' + data[5], 'rb')
            if cur_card[2] == 0:
                await bot.send_photo(message.chat.id, file,
                           f'<b>{data[1]}</b>\n<i>{data[2]}</i>\nЦена карточки: <b>{data[4]}</b>\n\nКоличество: <b>{cur_card[current+3][1]}</b>\nScore в этом сезоне: <b>{data1[0]}</b>',
                           parse_mode='html', reply_markup=showCardsMarkup)
            else:
                await bot.edit_message_media(chat_id=message.chat.id, message_id=message.message_id,
                                             media=types.InputMediaPhoto(file))
                await bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id,
                                               caption=f'<b>{data[1]}</b>\n<i>{data[2]}</i>\nЦена карточки: <b>{data[4]}</b>\n\nКоличество: <b>{cur_card[current+3][1]}</b>\nScore в этом сезоне: <b>{data1[0]}</b>',
                                               parse_mode='html', reply_markup=showCardsMarkup)
        elif current == cur_card[0] - 1:
            btnCurrentCard = types.InlineKeyboardButton(f'({current+1}/{pack_cards[message.chat.id][0]})', callback_data='nothing')
            showCardsMarkup.row(btnLeft, btnCurrentCard)
            showCardsMarkup.row(btnBack)
            file = open('./' + data[5], 'rb')
            await bot.edit_message_media(chat_id=message.chat.id, message_id=message.message_id, media = types.InputMediaPhoto(file))
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, caption=f'<b>{data[1]}</b>\n<i>{data[2]}</i>\nЦена карточки: <b>{data[4]}</b>\n\nКоличество: <b>{cur_card[current+3][1]}</b>\nScore в этом сезоне: <b>{data1[0]}</b>\n🍟 <i>Бро, это вся твоя коллекция</i>',
                           parse_mode='html', reply_markup=showCardsMarkup)
        else:
            btnCurrentCard = types.InlineKeyboardButton(f'({current+1}/{pack_cards[message.chat.id][0]})', callback_data='nothing')
            showCardsMarkup.row(btnLeft, btnCurrentCard, btnRight)
            showCardsMarkup.row(btnBack)
            file = open('./' + data[5], 'rb')
            await bot.edit_message_media(chat_id=message.chat.id, message_id=message.message_id,
                                   media=types.InputMediaPhoto(file))
            await bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id,
                                     caption=f'<b>{data[1]}</b>\n<i>{data[2]}</i>\nЦена карточки: <b>{data[4]}</b>\n\nКоличество: <b>{cur_card[current+3][1]}</b>\nScore в этом сезоне: <b>{data1[0]}</b>',
                                     parse_mode='html', reply_markup=showCardsMarkup)
    cur.close()
    con.close()



async def get_card(message: types.Message):
    global pass_times
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT pass_status FROM users WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data[0] == 0:
        cur.execute(f'SELECT * FROM drop_cards WHERE rarity = 5')
        data = cur.fetchall()
    else:
        cur.execute(f'SELECT * FROM drop_cards WHERE rarity = 5 AND pass_rarity = 0')
        data = cur.fetchall()
    if data is None:
        items = False
    else:
        items = True
    luck = random.randint(1,1000)
    if luck <= 500:
        rar = 1
    elif luck <= 750:
        rar = 2
    elif luck <= 900:
        rar = 3
    elif luck <= 999:
        rar = 4
    elif items == True:
        rar = 5
    else:
        rar = 4
    cur.execute(f'SELECT * FROM drop_cards WHERE rarity = {rar}')
    data = cur.fetchall()
    luck = random.randint(0, len(data)-1)
    file = open('./' + data[luck][5], 'rb')
    if data[luck][6] == 0:
        await bot.send_photo(message.chat.id, file,
                       f'🥡Держи бро, вот твоя карта!\n<b>{data[luck][1]}</b>\n<i>{data[luck][2]}</i>\nScore: <b>{data[luck][4]}</b>',
                       parse_mode='html')
        cur.execute(f'SELECT * FROM users_cards1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}')
        data3 = cur.fetchone()
        if data3 == None:
            cur.execute("INSERT INTO users_cards1 VALUES (?, ?, ?, ?)", (message.from_user.id, data[luck][0], 1, data[luck][3]))
            con.commit()
        else:
            cur.execute(f"UPDATE users_cards1 SET kolvo = kolvo + 1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}")
            con.commit()
    else:
        await bot.send_photo(message.chat.id, file,
                             f'🥡Держи бро, вот твоя карта!\n<b>{data[luck][1]}</b>\n<i>{data[luck][2]}</i>',
                             parse_mode='html')
        cur.execute(f'SELECT pass_status FROM users WHERE user_id = {message.chat.id}')
        data2 = cur.fetchone()
        status = data[luck][6]
        if data2[0] > data[luck][6]:
            status = data2[0]
        cur.execute(f'UPDATE users SET pay_pass = 1, pass_time = {int(time.time())}, push = 1, pass_status = {status} WHERE user_id = {message.chat.id}')
        con.commit()
    cur.execute(f'SELECT pay_pass FROM users WHERE user_id = {message.chat.id}')
    data1 = cur.fetchone()
    if data1[0] == True:
        push1 = 1
    else:
        push1 = 0
    cur.execute("UPDATE users SET push = '%i', get_cards_times = get_cards_times + 1, total_score = total_score + '%i', season_score = season_score + '%i', timer = '%i' WHERE user_id = '%i'" % (push1, data[luck][4], data[luck][4], message.date.timestamp(), message.from_user.id))
    con.commit()
    if rar == 5:
        cur.execute(f'SELECT username, f_name, pass_status FROM users WHERE user_id = {message.chat.id}')
        person = cur.fetchone()
        if data[luck][6] == 0:
            await bot.send_message(429229342, f'❗️Игрок <b>{person[1]}</b> (@{person[0]}) только что выбил реальную вещь (<b>{data[luck][1]}</b>)!', parse_mode='html')
        else:
            await bot.send_message(429229342,
                                   f'❗️Игрок <b>{person[1]}</b> (@{person[0]}) только что выбил себе pass на (<b>{pass_times[person[2] - 1]}</b>)!',
                                   parse_mode='html')
        cur.execute(f'DELETE FROM drop_cards WHERE id = {data[luck][0]}')
        con.commit()
    cur.close()
    con.close()

async def free_card(message: types.Message):
    global pass_times
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT pass_status FROM users WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data[0] == 0:
        cur.execute(f'SELECT * FROM drop_cards WHERE rarity = 5')
        data = cur.fetchall()
    else:
        cur.execute(f'SELECT * FROM drop_cards WHERE rarity = 5 AND pass_rarity = 0')
        data = cur.fetchall()
    if data is None:
        items = False
    else:
        items = True
    luck = random.randint(1,1000)
    if luck <= 500:
        rar = 1
    elif luck <= 750:
        rar = 2
    elif luck <= 900:
        rar = 3
    elif luck <= 999:
        rar = 4
    elif items == True:
        rar = 5
    else:
        rar = 4
    cur.execute(f'SELECT * FROM drop_cards WHERE rarity = {rar}')
    data = cur.fetchall()
    luck = random.randint(0, len(data)-1)
    file = open('./' + data[luck][5], 'rb')
    if data[luck][6] == 0:
        await bot.send_photo(message.chat.id, file,
                             f'🥡Держи бро, вот твоя карта!\n<b>{data[luck][1]}</b>\n<i>{data[luck][2]}</i>\nScore: <b>{data[luck][4]}</b>',
                             parse_mode='html')
        cur.execute(f'SELECT * FROM users_cards1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}')
        data3 = cur.fetchone()
        if data3 == None:
            cur.execute("INSERT INTO users_cards1 VALUES (?, ?, ?, ?)",
                        (message.from_user.id, data[luck][0], 1, data[luck][3]))
            con.commit()
        else:
            cur.execute(
                f"UPDATE users_cards1 SET kolvo = kolvo + 1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}")
            con.commit()
    else:
        await bot.send_photo(message.chat.id, file,
                             f'🥡Держи бро, вот твоя карта!\n<b>{data[luck][1]}</b>\n<i>{data[luck][2]}</i>',
                             parse_mode='html')
        cur.execute(f'SELECT pass_status FROM users WHERE user_id = {message.chat.id}')
        data2 = cur.fetchone()
        status = data[luck][6]
        if data2[0] > data[luck][6]:
            status = data2[0]
        cur.execute(
            f'UPDATE users SET pay_pass = 1, pass_time = {int(time.time())}, push = 1, pass_status = {status} WHERE user_id = {message.chat.id}')
        con.commit()
    cur.execute("UPDATE users SET get_cards_times = get_cards_times + 1, total_score = total_score + '%i', season_score = season_score + '%i' WHERE user_id = '%i'" % (data[luck][4], data[luck][4], message.from_user.id))
    con.commit()
    if rar == 5:
        cur.execute(f'SELECT username, f_name, pass_status FROM users WHERE user_id = {message.chat.id}')
        person = cur.fetchone()
        if data[luck][6] == 0:
            await bot.send_message(429229342,
                                   f'❗️Игрок <b>{person[1]}</b> (@{person[0]}) только что выбил реальную вещь (<b>{data[luck][1]}</b>)!',
                                   parse_mode='html')
        else:
            await bot.send_message(429229342,
                                   f'❗️Игрок <b>{person[1]}</b> (@{person[0]}) только что выбил себе pass на (<b>{pass_times[person[2] - 1]}</b>)!',
                                   parse_mode='html')
        cur.execute(f'DELETE FROM drop_cards WHERE id = {data[luck][0]}')
        con.commit()
    cur.close()
    con.close()

async def get_card_from_promo(message: types.Message, card_id: int):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM drop_cards WHERE id = {card_id}')
    data = cur.fetchone()
    file = open('./' + data[5], 'rb')
    await bot.send_photo(message.chat.id, file,
                   f'🥡Держи бро, вот твоя карта!\n<b>{data[1]}</b>\n<i>{data[2]}</i>\nScore: <b>{data[4]}</b>',
                   parse_mode='html', reply_markup=basicMarkup)
    cur.execute(
        f'UPDATE users SET get_cards_times = get_cards_times + 1, total_score = total_score + {data[4]}, season_score = season_score + {data[4]} WHERE user_id = {message.chat.id}')
    con.commit()
    cur.execute(f'SELECT * FROM users_cards1 WHERE user_id = {message.chat.id} AND card_id = {data[0]}')
    data3 = cur.fetchone()
    if data3 == None:
        cur.execute("INSERT INTO users_cards1 VALUES (?, ?, ?, ?)",
                    (message.from_user.id, data[0], 1, data[3]))
        con.commit()
    else:
        cur.execute(
            f"UPDATE users_cards1 SET kolvo = kolvo + 1 WHERE user_id = {message.chat.id} AND card_id = {data[0]}")
        con.commit()
    if data[3] == 5:
        cur.execute(f'SELECT username, f_name FROM users WHERE user_id = {message.chat.id}')
        person = cur.fetchone()
        await bot.send_message(429229342,
                               f'❗️Игрок <b>{person[1]}</b> (@{person[0]}) только что получил реальную вещь с помощью промокода(<b>{data[1]}</b>)!',
                               parse_mode='html')
        cur.execute(f'DELETE FROM drop_cards WHERE id ={data[0]}')
        con.commit()
    cur.close()
    con.close()

async def get_craft_card(message: types.Message, rar):
    con1 = sqlite3.connect('tobless.sql')
    cur1 = con1.cursor()
    cur1.execute(f'SELECT * FROM drop_cards WHERE rarity = {rar+1}')
    data = cur1.fetchall()
    luck = random.randint(0, len(data)-1)
    file = open('./' + data[luck][5], 'rb')
    if data[luck][6] == 0:
        await bot.send_photo(message.chat.id, file,
                       f'🥡Держи бро, вот твоя карта!\n<b>{data[luck][1]}</b>\n<i>{data[luck][2]}</i>\nScore: <b>{data[luck][4]}</b>',
                       parse_mode='html')
        cur1.execute(f'SELECT * FROM users_cards1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}')
        data3 = cur1.fetchone()
        if data3 == None:
            cur1.execute("INSERT INTO users_cards1 VALUES (?, ?, ?, ?)", (message.from_user.id, data[luck][0], 1, data[luck][3]))
            con1.commit()
        else:
            cur1.execute(f"UPDATE users_cards1 SET kolvo = kolvo + 1 WHERE user_id = {message.chat.id} AND card_id = {data[luck][0]}")
            con1.commit()
    cur1.execute("UPDATE users SET total_score = total_score + '%i', season_score = season_score + '%i' WHERE user_id = '%i'" % (data[luck][4], data[luck][4], message.from_user.id))
    con1.commit()
    cur1.close()
    con1.close()


@dp.message_handler(commands=['start'])
async def main(message: types.Message):
    #await bot.send_message(message.chat.id, f'{int(time.time())}')
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    storage = shelve.open('shelve')
    storage[str(message.chat.id)] = 'init'
    storage.close()
    await create_sql()
    cur.execute(f'SELECT * FROM banned WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data == None:
        cur.execute(f'SELECT user_id FROM users WHERE user_id = {message.chat.id}')
        data = cur.fetchone()
        cur.close()
        con.close()
        if data is None:
            await register_user(message)
            args = message.get_args()
            if args:
                con = sqlite3.connect('tobless.sql')
                cur = con.cursor()
                cur.execute("INSERT INTO refers VALUES (?, ?, 0)", (
                message.chat.id, int(args)))
                con.commit()
        await bot.send_message(message.chat.id, f'🙆🏼‍♂Welcome to ToBlessCartoon, <b>{message.from_user.first_name}</b>!\n\n🌍Это простая игра по мотивам мировой моды\n\n🥪Собирай карточки топового шмота, копи очки, обходи\n\nдрузей в рейтинге и участвуй в конкурсах!\n\n🍜 У нас ты можешь выбить себе реальные вещи, которые можешь носить сам или продать в будущем.', parse_mode='html', reply_markup=basicMarkup)
    else:
        await bot.send_message(message.chat.id, f'❌ Вы были забанены!')

@dp.message_handler(commands=['semechka2278'])
async def main(message: types.Message):
    storage = shelve.open('shelve')
    state = storage[str(message.chat.id)]
    if state != 'init':
        pass
        storage.close()
    else:
        await bot.send_message(message.chat.id, 'Добро пожаловать в админку. Выбери нужное действие!',
                         reply_markup=adminMarkup)
        storage[str(message.chat.id)] = 'admin'
        storage.close()

@dp.callback_query_handler(lambda callback: callback.data == 'move_right')
async def callback_move_right(callback):
    global pack_cards
    info = pack_cards[callback.message.chat.id]
    info[1] += 1
    info[2] = 1
    pack_cards[callback.message.chat.id] = info
    await show_cards(callback.message)

@dp.callback_query_handler(lambda callback: callback.data == 'move_left')
async def callback_move_left(callback):
    global pack_cards
    info = pack_cards[callback.message.chat.id]
    info[1] -= 1
    pack_cards[callback.message.chat.id] = info
    await show_cards(callback.message)

@dp.callback_query_handler(lambda callback: callback.data == 'move_back')
async def callback_move_back(callback):
    global pack_cards
    pack_cards.pop(callback.message.chat.id)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

@dp.callback_query_handler(lambda callback: callback.data == 'menu_back')
async def callback_move_back(callback):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

@dp.callback_query_handler(lambda callback: callback.data == 'accept_del')
async def callback_accept_del(callback):
    global chosen_card
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()

    storage = shelve.open('shelve')
    storage[str(callback.message.chat.id)] = 'admin'
    storage.close()

    cur.execute(f'DELETE FROM drop_cards WHERE id = {chosen_card}')
    con.commit()
    await bot.send_message(callback.message.chat.id, 'Карточка была успешно удалена!', reply_markup=adminMarkup)
    chosen_card = -1
    cur.close()
    con.close()


@dp.callback_query_handler(lambda callback: callback.data == 'pay_pass')
async def callback_pay_pass(callback):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT pay_pass FROM users WHERE user_id = {callback.message.chat.id}')
    data = cur.fetchone()
    if data[0] == 0:
        await bot.send_invoice(callback.message.chat.id, 'Подписка Pay Pass', '• 🎃 3 часа ожидания следующей карты, вместо 4\n• 🤖 Уведомление о следующей попытке.\n• Возможность создать свой 👻 Клан и покорять вершины вместе со своими друзьями.', 'invoice', '390540012:LIVE:38041', 'rub', [types.LabeledPrice('Оформить подписку на месяц', 150 * 100)])
    else:
        cur.execute(f'SELECT pass_time FROM users WHERE user_id = {callback.message.chat.id}')
        data = cur.fetchone()
        diff = int(callback.message.date.timestamp()) - data[0]
        need = 2592000
        diff = need - diff
        days = diff // 86400
        hours = (diff % 86400) // 3600
        mins = (diff - 86400 * days - 3600 * hours) // 60
        sec = diff - 86400 * days - 3600 * hours - 60 * mins
        await bot.send_message(callback.message.chat.id, f'Бро, ты уже приобрел Pay Pass и срок твоей подписки пока не истек!\n⏳ Осталось еще <b>{days} д {hours} ч {mins} мин {sec} сек</b>',
                         parse_mode='html')
        cur.close()
        con.close()

@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(query):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message_handler(content_types=['successful_payment'])
async def success(message):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'UPDATE users SET pay_pass = {True}, pass_time = {message.date.timestamp()} WHERE user_id = {message.chat.id}')
    con.commit()
    await bot.send_message(message.chat.id, '🎉 Поздравляю, ты только что получил подписку Pay Pass на 30 дней! Теперь пришло время воспользоваться полученными преимуществами!')
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'del_card')
async def callback_del_card(callback):
    global colors
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()

    storage = shelve.open('shelve')
    storage[str(callback.message.chat.id)] = 'admin_choose_card'
    storage.close()

    cur.execute('SELECT * FROM drop_cards')
    data = cur.fetchall()
    card_list = 'Список имеющихся карт:\n\n'
    info = []
    for el in data:
        card_list1 = card_list
        card_list += f'{el[0]} - {el[1]} (редкость: {colors[int(el[3])-1]}, score: {el[4]})\n'
        if len(card_list) > 4096:
            info.append(card_list1)
            card_list = f'{el[0]} - {el[1]} (редкость: {colors[int(el[3])-1]}, score: {el[4]})\n'
    info.append(card_list)
    await bot.send_message(callback.message.chat.id, 'Напиши цифрой номер карточки которую хочешь удалить')
    for el in info:
        await bot.send_message(callback.message.chat.id, el)
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'add_promo')
async def callback_add_promo(callback):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()

    storage = shelve.open('shelve')
    storage[str(callback.message.chat.id)] = 'admin_choose_card_for_promo'
    storage.close()

    cur.execute('SELECT * FROM drop_cards')
    data = cur.fetchall()
    card_list = ''
    for el in data:
        card_list += f'{el[0]} - {el[1]} (редкость: {colors[int(el[3])-1]}, score: {el[4]})\n'
    await bot.send_message(callback.message.chat.id, 'Напиши цифрой номер карточки, для которой хочешь добавить промокод')
    await bot.send_message(callback.message.chat.id, 'Список имеющихся карт:\n\n' + card_list)
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'accept_promo')
async def callback_add_promo(callback):

    storage = shelve.open('shelve')
    storage[str(callback.message.chat.id)] = 'admin_write_promo'
    storage.close()

    await bot.send_message(callback.message.chat.id, 'Отлично, теперь напиши сам промокод для выбранной карточки')

@dp.callback_query_handler(lambda callback: callback.data == 'show_promos')
async def callback_add_promo(callback):
    global colors
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    data = []

    cur.execute('SELECT * FROM promos')
    cards = cur.fetchall()
    for i in cards:
        cur.execute(f'SELECT title, rarity, score FROM drop_cards WHERE id = {i[1]}')
        card_now = cur.fetchone()
        data.append([i[0], i[2], i[3]])
        for el in card_now:
            data[-1].append(el)
    promo_list = ''
    for el in data:
        promo_list += f'{el[0]} - <b>{el[1]}</b> (Осталось <b>{el[2]}</b>) - {el[3]} (редкость: {colors[int(el[4])-1]}, score: {el[5]})\n'


    await bot.send_message(callback.message.chat.id, 'Список имеющихся промокодов:\n\n' + promo_list, parse_mode='html', reply_markup=adminMarkup)
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'users_info')
async def callback_add_promo(callback):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    data = []

    cur.execute('SELECT user_id FROM users')
    data = cur.fetchall()
    t = time.time()
    cur.execute(f'SELECT user_id FROM users WHERE {t} - timer <= 86400')
    data1 = cur.fetchall()
    await bot.send_message(callback.message.chat.id, f'Всего зарегистрировано пользователей: <b>{len(data)}</b>\nПолучило карт по кнопке за последние сутки: <b>{len(data1)}</b>', parse_mode='html', reply_markup=adminMarkup)
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'use_promo')
async def callback_add_promo(callback):

    storage = shelve.open('shelve')
    storage[str(callback.message.chat.id)] = 'write_promo'
    storage.close()

    await bot.send_message(callback.message.chat.id, '🧃 Йо, бро, здесь ты можешь получить карточку вне очереди. Если у тебя есть промокод, введи его в своем следующем сообщении!')

@dp.callback_query_handler(lambda callback: callback.data == 'choose_top')
async def callback_add_promo(callback):
    await bot.send_message(callback.message.chat.id, '💬 Какой рейтинг ты хочешь посмотреть?', reply_markup=topMarkup)

@dp.callback_query_handler(lambda callback: callback.data == 'top_season')
async def callback_add_promo(callback):
    global medals
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute('SELECT user_id, season_score FROM users ORDER BY season_score DESC')
    data = cur.fetchall()
    for i in range(len(data)):
        if data[i][0] == callback.message.chat.id:
            place = i + 1
            own_score = data[i][1]
    cur.execute('SELECT username, season_score FROM users ORDER BY season_score DESC LIMIT 10')
    data = cur.fetchall()
    output = '🏆 Топ-10 игроков в этом сезоне\n\n'
    for i in range(len(data)):
        if i <= 2:
            output += medals[i]
        else:
            output += str(i+1)
            output += '.'
        output += f'@{data[i][0]} (Score: <b>{data[i][1]}</b>)\n'
    output += f'\nТы на <b>{place}-ом</b> месте (Score: <b>{own_score}</b>)'
    await bot.send_message(callback.message.chat.id, output, parse_mode='html')

@dp.callback_query_handler(lambda callback: callback.data == 'top_all')
async def callback_add_promo(callback):
    global medals
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute('SELECT user_id, total_score FROM users ORDER BY total_score DESC')
    data = cur.fetchall()
    for i in range(len(data)):
        if data[i][0] == callback.message.chat.id:
            place = i + 1
            own_score = data[i][1]
    cur.execute('SELECT username, total_score FROM users ORDER BY total_score DESC LIMIT 10')
    data = cur.fetchall()
    output = '🏆 Топ-10 игроков за все время\n\n'
    for i in range(len(data)):
        if i <= 2:
            output += medals[i]
        else:
            output += str(i+1)
            output += '.'
        output += f'@{data[i][0]} (Score: <b>{data[i][1]}</b>)\n'
    output += f'\nТы на <b>{place}-ом</b> месте (Score: <b>{own_score}</b>)'
    await bot.send_message(callback.message.chat.id, output, parse_mode='html')

@dp.callback_query_handler(lambda callback: callback.data == 'my_ref')
async def callback_my_ref(callback):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT refs, free, level, cur_level FROM users WHERE user_id = {callback.message.chat.id}')
    data = cur.fetchone()
    link = await get_start_link(callback.message.chat.id)
    output = f'🫂 Бро, это твоя реферальная программа\n\nИзначально за каждых <b>5</b> друзей, которые начнут играть в ToBless Cartoon по твоей ссылке ты получишь <b>бесплатный прокрут вне очереди</b> по кнопке "🃏 Получить карту", тем самым увеличив свои шансы на выпадение реальной вещи 👕 После каждых <b>50</b> полученных прокрутов кол-во необходимых рефералов для нового прокручивания будет уменьшаться на единицу!\n\n❗️ Всего за сезон можно получить максимум <b>400</b> прокрутов\n❗️Реферал заситывается только после того, как получит свою <b>первую карту</b>\n\n🔗Ссылка: {link}\n\n• Осталось free прокрутов: <b>{data[1]}</b>\n• По твоей ссылке играют: <b>{data[0]}</b> друзей\n• Рефералов до следующего прокрута: <b>{data[2] - data[3]}</b>\n'
    await bot.send_message(callback.message.chat.id, output, parse_mode='html')
    cur.close()
    con.close()

@dp.callback_query_handler(lambda callback: callback.data == 'rules')
async def callback_my_ref(callback):
    output = f'📌 По правилам игры, участники могут выбить реальную вещь несколькими способами. Прокручивать попытки и занимать лидирующие места в топе за сезон.\n\n📌 Очки - даются за полученные карточки через промокоды и через прокруты. За очки вы можете занимать место в топе\n\n📌 Рефералы - люди, которые начали играть по вашей ссылке. Строго запрещена накрутка рефералов (ботов), карается баном и аннулированием результатов.\n\n📌 Пользоваться твинками для трейдов также запрещено, карается аннулированием результатов\n\n📌 Слив промокодов запрещен, карается баном. Если слив происходит из VIP канала людей оплативших Pay Pass, то он снимается.'
    await bot.send_message(callback.message.chat.id, output, parse_mode='html')

@dp.callback_query_handler(lambda callback: callback.data == 'craft')
async def callback_my_ref(callback):
    con2 = sqlite3.connect('tobless.sql')
    cur2 = con2.cursor()
    cur2.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 1')
    data = cur2.fetchall()
    data1 = [int(el[0]) for el in data]
    white_duplicates = sum(data1) - len(data1)
    cur2.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 2')
    data = cur2.fetchall()
    data1 = [int(el[0]) for el in data]
    blue_duplicates = sum(data1) - len(data1)
    cur2.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 3')
    data = cur2.fetchall()
    data1 = [int(el[0]) for el in data]
    purple_duplicates = sum(data1) - len(data1)
    output = f'🍕 Бро, это крафт, здесь ты можешь создавать из повторных карточек карты редкостью выше\n\n<b>У тебя имеется на данный момент:</b>\n⚪️ дубликатов: <b>{white_duplicates}</b>\n🔵 дубликатов: <b>{blue_duplicates}</b>\n🟣 дубликатов: <b>{purple_duplicates}</b>\n'
    await bot.send_message(callback.message.chat.id, output, parse_mode='html', reply_markup=craftMarkup)
    cur2.close()
    con2.close()

@dp.callback_query_handler(lambda callback: callback.data == 'craft_white')
async def callback_white_craft(callback: types.CallbackQuery):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 1')
    data = cur.fetchall()
    data1 = [int(el[0]) for el in data]
    white_duplicates = sum(data1) - len(data1)
    if white_duplicates < 10:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Недостаточно дубликатов", show_alert=True)
        cur.close()
        con.close()
    else:
        ten = 10
        while ten > 0:
            cur.execute(f'SELECT card_id, kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 1 AND kolvo > 1')
            data = cur.fetchone()
            data1 = list(data)
            while ten > 0 and data1[1] > 1:
                ten -= 1
                data1[1] -= 1
            cur.execute(f'UPDATE users_cards1 SET kolvo = {data1[1]} WHERE user_id = {callback.message.chat.id} AND card_id = {data1[0]}')
            con.commit()
        cur.close()
        con.close()
        await get_craft_card(callback.message, 1)

@dp.callback_query_handler(lambda callback: callback.data == 'craft_blue')
async def callback_blue_craft(callback: types.CallbackQuery):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 2')
    data = cur.fetchall()
    data1 = [int(el[0]) for el in data]
    white_duplicates = sum(data1) - len(data1)
    if white_duplicates < 10:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Недостаточно дубликатов", show_alert=True)
        cur.close()
        con.close()
    else:
        ten = 10
        while ten > 0:
            cur.execute(f'SELECT card_id, kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 2 AND kolvo > 1')
            data = cur.fetchone()
            data1 = list(data)
            while ten > 0 and data1[1] > 1:
                ten -= 1
                data1[1] -= 1
            cur.execute(f'UPDATE users_cards1 SET kolvo = {data1[1]} WHERE user_id = {callback.message.chat.id} AND card_id = {data1[0]}')
            con.commit()
        cur.close()
        con.close()
        await get_craft_card(callback.message, 2)

@dp.callback_query_handler(lambda callback: callback.data == 'craft_purple')
async def callback_blue_craft(callback: types.CallbackQuery):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 3')
    data = cur.fetchall()
    data1 = [int(el[0]) for el in data]
    white_duplicates = sum(data1) - len(data1)
    if white_duplicates < 10:
        await bot.answer_callback_query(callback_query_id=callback.id, text="⚠️ Недостаточно дубликатов", show_alert=True)
        cur.close()
        con.close()
    else:
        ten = 10
        while ten > 0:
            cur.execute(f'SELECT card_id, kolvo FROM users_cards1 WHERE user_id = {callback.message.chat.id} AND rarity = 3 AND kolvo > 1')
            data = cur.fetchone()
            data1 = list(data)
            while ten > 0 and data1[1] > 1:
                ten -= 1
                data1[1] -= 1
            cur.execute(f'UPDATE users_cards1 SET kolvo = {data1[1]} WHERE user_id = {callback.message.chat.id} AND card_id = {data1[0]}')
            con.commit()
        cur.close()
        con.close()
        await get_craft_card(callback.message, 3)

@dp.callback_query_handler(lambda callback: True)
async def callback_message(callback):
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    storage = shelve.open('shelve')
    state = storage[str(callback.message.chat.id)]
    if callback.data == 'add_card':
        if state != 'admin':
            pass
            storage.close()
        else:
            await bot.send_message(callback.message.chat.id, 'Какую карточку хочешь добавить?', reply_markup=chooseCardTypeMarkup)
            storage.close()
    elif callback.data == 'default_card':
        await bot.send_message(callback.message.chat.id, 'Пришли изображение карточки без текста')
        storage[str(callback.message.chat.id)] = 'admin_add_photo'
        storage.close()
    elif callback.data == 'pass_card':
        await bot.send_message(callback.message.chat.id, 'Пришли изображение карточки без текста')
        storage[str(callback.message.chat.id)] = 'admin_add_pass_photo'
        storage.close()
    elif callback.data == 'right_card':
        cur.execute('SELECT * FROM cards ORDER BY id DESC LIMIT 1')
        data = cur.fetchone()
        cur.execute("INSERT INTO drop_cards VALUES (?, ?, ?, ?, ?, ?, ?)", (
        data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
        con.commit()
        storage[str(callback.message.chat.id)] = 'admin'
        storage.close()
        await bot.send_message(callback.message.chat.id, 'Карточка была удачно добавлена!',
                         reply_markup=adminMarkup)
    elif callback.data == 'change_card':
        await bot.send_message(callback.message.chat.id, 'Выбери какой параметр карточки хочешь поменять', reply_markup=changeCardMarkup)
        storage.close()
    elif callback.data == 'change_pass_card':
        await bot.send_message(callback.message.chat.id, 'Выбери какой параметр карточки хочешь поменять', reply_markup=changePassCardMarkup)
        storage.close()
    elif callback.data == 'change_photo':
        await bot.send_message(callback.message.chat.id, 'Пришли изображение карточки без текста')
        storage[str(callback.message.chat.id)] = 'admin_change_photo'
        storage.close()
    elif callback.data == 'change_name':
        await bot.send_message(callback.message.chat.id, 'Напишите новое название карточки!')
        storage[str(callback.message.chat.id)] = 'admin_change_title'
        storage.close()
    elif callback.data == 'change_desc':
        await bot.send_message(callback.message.chat.id, 'Напишите новое описание карточки!')
        storage[str(callback.message.chat.id)] = 'admin_change_desc'
        storage.close()
    elif callback.data == 'change_rar':
        await bot.send_message(callback.message.chat.id, 'Напишите новую редкость карточки цифрой от 1 до 5, где:\n1 - ⚪️\n2 - 🔵\n3 - 🟣\n4 - 🟡\n5 - real вещь')
        storage[str(callback.message.chat.id)] = 'admin_change_rar'
        storage.close()
    elif callback.data == 'change_price':
        await bot.send_message(callback.message.chat.id, 'Напишите новую цену карточки!')
        storage[str(callback.message.chat.id)] = 'admin_change_price'
        storage.close()
    elif callback.data == 'change_pass_rar':
        await bot.send_message(callback.message.chat.id, 'Укажите цифрой от 1 до 3 новую длительность Pass для карты, где:\n1 - день\n2 - неделя\n3 - месяц')
        storage[str(callback.message.chat.id)] = 'admin_change_pass_rar'
        storage.close()
    cur.close()
    con.close()




@dp.message_handler(content_types=['photo'])
async def handle_docs_document(message: types.Message):
    storage = shelve.open('shelve')
    state = storage[str(message.chat.id)]
    if state != 'admin_add_photo' and state != 'admin_change_photo' and state != 'admin_add_pass_photo':
        pass
        storage.close()
    else:
        con = sqlite3.connect('tobless.sql')
        cur = con.cursor()
        cur.execute('SELECT * FROM cards ORDER BY id DESC LIMIT 1')
        data = cur.fetchone()
        if data == None:
            photo_name = '1.jpeg'
            photo_id = 1
        else:
            photo_id = data[0] + 1
            prev_photo = data[5]
            jpeg = prev_photo.find('.')
            photo_name = str(int(prev_photo[:jpeg])+1) + '.jpeg'

        file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(photo_name, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())
        if state == 'admin_add_photo' or state == 'admin_add_pass_photo':
            cur.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?)", (photo_id, 'start', 'start', 5, 0, photo_name, 0))
            con.commit()
            await message.reply("Фото было успешно добавлено! Теперь напишите название карточки")
            if state == 'admin_add_photo':
                storage[str(message.chat.id)] = 'admin_add_title'
            else:
                storage[str(message.chat.id)] = 'admin_add_pass_title'
        else:
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE cards SET path_to = "{photo_name}" WHERE id = {data[0]}')
            con.commit()
            await print_added_card(message)

        cur.close()
        con.close()
        storage.close()

@dp.message_handler()
async def main(message):
    global chosen_card, pack_cards, card_for_promo
    await register_user(message)
    storage = shelve.open('shelve')
    state = storage[str(message.chat.id)]
    con = sqlite3.connect('tobless.sql')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM banned WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data == None:
        if message.text.lower() == 'привет':
            storage = shelve.open('shelve')
            storage[str(message.chat.id)] = 'init'
            storage.close()
            await create_sql()
            await bot.send_message(message.chat.id,
                             f'🙆🏼‍♂Welcome to ToBlessCartoon, <b>{message.from_user.first_name}</b>!\n\n🌍Это простая игра по мотивам мировой моды\n\n🥪Собирай карточки топового шмота, копи очки, обходи\n\nдрузей в рейтинге и участвуй в конкурсах!\n\n🍜 У нас ты можешь выбить себе реальные вещи, которые можешь носить сам или продать в будущем.',
                             parse_mode='html', reply_markup=basicMarkup)
        elif message.text == '🃏 Получить карту':
            first = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.chat.id)
            second = await bot.get_chat_member(chat_id=CHANNEL_ID1, user_id=message.chat.id)
            if check_sub_channel(first) and check_sub_channel(second):
                '''con = sqlite3.connect('tobless.sql')
                cur = con.cursor()'''
                #cur.execute(f'UPDATE users SET username = "{message.from_user.username}", f_name = "{message.from_user.first_name}", l_name = "{message.from_user.last_name}" WHERE user_id = {message.from_user.id}')
                #con.commit()
                cur.execute(f'SELECT username, f_name, l_name FROM users WHERE user_id = {message.from_user.id}')
                data = cur.fetchone()
                if data[0] != message.from_user.username:
                    cur.execute(f'UPDATE users SET username = "{message.from_user.username}" WHERE user_id = {message.from_user.id}')
                    con.commit()
                if data[1] != message.from_user.first_name:
                    cur.execute(f'UPDATE users SET f_name = "{message.from_user.first_name}" WHERE user_id = {message.from_user.id}')
                    con.commit()
                if data[2] != message.from_user.last_name:
                    cur.execute(f'UPDATE users SET l_name = "{message.from_user.last_name}" WHERE user_id = {message.from_user.id}')
                    con.commit()
                cur.execute(f'SELECT referer_id FROM refers WHERE referal_id = {message.chat.id} AND commited = 0')
                data = cur.fetchone()
                if data != None:
                    cur.execute(f'UPDATE refers SET commited = 1 WHERE referal_id = {message.chat.id}')
                    con.commit()
                    cur.close()
                    con.close()
                    await add_referal(message, data[0])
                    con = sqlite3.connect('tobless.sql')
                    cur = con.cursor()
                cur.execute(f'SELECT free FROM users WHERE user_id = {message.from_user.id}')
                data = cur.fetchone()
                if data[0] > 0:
                    await free_card(message)
                    cur.execute(f'UPDATE users SET free = free - 1 WHERE user_id = {message.from_user.id}')
                    con.commit()
                else:
                    cur.execute(f'SELECT timer, pay_pass FROM users WHERE user_id = {message.from_user.id}')
                    data = cur.fetchone()
                    if data[0] == 0:
                        await get_card(message)
                    else:
                        if data[1] == True:
                            need = 3600 * 3
                        else:
                            need = 3600 * 4
                        diff = int(message.date.timestamp()) - data[0]
                        if diff > need:
                            await get_card(message)
                        else:
                            diff = need - diff
                            hours = diff // 3600
                            mins = (diff % 3600) // 60
                            sec = diff - 3600*hours - 60 * mins
                            await bot.send_message(message.chat.id, f'Не так быстро!\nСледующая попытка будет доступна через <b>{hours} ч {mins} мин {sec} сек</b>', parse_mode='html')
                '''cur.close()
                con.close()'''
            else:
                await bot.send_message(message.from_user.id, notsub_message, reply_markup=checksub, parse_mode='html')
        elif message.text == '🌮 Мои карты':
            '''con = sqlite3.connect('tobless.sql')
            cur = con.cursor()'''
            cur.execute(f'SELECT card_id, kolvo FROM users_cards1 WHERE user_id = {message.from_user.id}')
            data = cur.fetchall()
            user_cards = []
            if data != None:
                user_cards.append(len(data))
                user_cards.append(0)
                user_cards.append(0)
                for el in data:
                    user_cards.append(list(el))
                pack_cards[message.from_user.id] = user_cards
                await show_cards(message)
            else:
                await bot.send_message(message.chat.id, '⚠️ Бро, у тебя пока что нет карточек в коллекции. Чтобы пополнить её, скорее испытывай свою удачу, нажав по кнопке "🃏 Получить карту"!')
        elif message.text == 'Ⓜ️ Меню':
            await bot.send_message(message.chat.id, '📢 Выберите действие по кнопкам ниже', reply_markup=menuMarkup)
        elif state == 'admin_add_title' or state == 'admin_change_title' or state == 'admin_add_pass_title':
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            title = message.text.strip()
            cur.execute(f'UPDATE cards SET title = "{title}" WHERE id = {data[0]}')
            con.commit()
            if state == 'admin_add_title' or state == 'admin_add_pass_title':
                await bot.send_message(message.chat.id, 'Теперь введите описание карточки')
                if state == 'admin_add_title':
                    storage[str(message.chat.id)] = 'admin_add_desc'
                else:
                    storage[str(message.chat.id)] = 'admin_add_pass_desc'
            elif state == 'admin_change_title':
                await print_added_card(message)
            storage.close()
        elif state == 'admin_add_desc' or state == 'admin_change_desc' or state == 'admin_add_pass_desc':
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE cards SET description = "{message.text.strip()}" WHERE id = {data[0]}')
            con.commit()
            if state == 'admin_add_desc':
                await bot.send_message(message.chat.id, 'Отлично, теперь укажите цифрой от 1 до 5 редкость карточки, где:\n1 - ⚪️\n2 - 🔵\n3 - 🟣\n4 - 🟡\n5 - real вещь')
                storage[str(message.chat.id)] = 'admin_add_rar'
            elif state == 'admin_add_pass_desc':
                await bot.send_message(message.chat.id,
                                       'Отлично, теперь укажите цифрой от 1 до 3 длительность Pass для карты, где:\n1 - день\n2 - неделя\n3 - месяц')
                storage[str(message.chat.id)] = 'admin_add_pass_rar'
            elif state == 'admin_change_desc':
                await print_added_card(message)
            storage.close()
        elif state == 'admin_add_rar' or state == 'admin_change_rar':
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE cards SET rarity = {message.text.strip()} WHERE id = {data[0]}')
            con.commit()
            if state == 'admin_add_rar':
                await bot.send_message(message.chat.id, 'Отлично, осталось только указать числом(!) стоимость данной карточки!')
                storage[str(message.chat.id)] = 'admin_add_price'
            elif state == 'admin_change_rar':
                await print_added_card(message)
            storage.close()
        elif state == 'admin_add_pass_rar' or state == 'admin_change_pass_rar':
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE cards SET pass_rarity = {message.text.strip()} WHERE id = {data[0]}')
            con.commit()
            await print_added_card(message)
            storage.close()
        elif state == 'admin_add_price' or state == 'admin_change_price':
            cur.execute('SELECT id FROM cards ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE cards SET score = {message.text.strip()} WHERE id = {data[0]}')
            con.commit()
            await print_added_card(message)
            storage.close()
        elif state == 'admin_choose_card':
            chosen_card = int(message.text.strip())
            '''con = sqlite3.connect('tobless.sql')
            cur = con.cursor()'''
            cur.execute(f'SELECT * FROM drop_cards WHERE id = {chosen_card}')
            data = cur.fetchone()
            file = open('./' + data[5], 'rb')
            await bot.send_photo(message.chat.id, file,
                           f'🥡Держи бро, вот твоя карта!\n<b>{data[1]}</b>\n<i>{data[2]}</i>\nScore: <b>{data[4]}</b>',
                           parse_mode='html')
            await bot.send_message(message.chat.id, 'Перед вами выбранная карта на удаление. Вы уверены что хотите её удалить?', reply_markup=acceptDelMarkup)
            '''cur.close()
            con.close()'''
            storage.close()
        elif state == 'admin_choose_card_for_promo':
            card_for_promo = int(message.text.strip())
            cur.execute(f'SELECT * FROM drop_cards WHERE id = {card_for_promo}')
            data = cur.fetchone()
            file = open('./' + data[5], 'rb')
            await bot.send_photo(message.chat.id, file,
                           f'🥡Держи бро, вот твоя карта!\n<b>{data[1]}</b>\n<i>{data[2]}</i>\nScore: <b>{data[4]}</b>',
                           parse_mode='html')
            await bot.send_message(message.chat.id, 'Перед вами выбранная карта для промокода. Все верно?',
                             reply_markup=acceptAddPromoMarkup)
            storage.close()
        elif state == 'admin_write_promo':
            cur.execute('SELECT * FROM promos ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            if data == None:
                promo_id = 1
            else:
                promo_id = data[0] + 1
            cur.execute("INSERT INTO promos VALUES (?, ?, ?, 0)", (promo_id, card_for_promo, message.text))
            con.commit()
            await bot.send_message(message.chat.id, 'Отлично, теперь введи допустимое количество использований данного промокода!')
            card_for_promo = -1
            storage[str(message.chat.id)] = 'admin_write_promo_times'
            storage.close()
        elif state == 'admin_write_promo_times':
            cur.execute('SELECT id FROM promos ORDER BY id DESC LIMIT 1')
            data = cur.fetchone()
            cur.execute(f'UPDATE promos SET times = {int(message.text.strip())} WHERE id = {data[0]}')
            con.commit()
            await bot.send_message(message.chat.id, 'Промокод был удачно добавлен!',
                             reply_markup=adminMarkup)
            storage[str(message.chat.id)] = 'admin'
            storage.close()
        elif state == 'write_promo':
            text = str(message.text)
            cur.execute(f'SELECT card_id, times FROM promos WHERE promo = "{message.text}"')
            data = cur.fetchone()
            if data != None:
                cur.execute(f'SELECT promo FROM users_promos WHERE user_id = {message.from_user.id}')
                data1 = cur.fetchall()
                repeat = False
                if data1 != None:
                    for i in range(len(data1)):
                        if data1[i][0] == text:
                            repeat = True
                            break
                if repeat == True:
                    await bot.send_message(message.chat.id, 'Ты уже использовал данный промокод! 🤕',
                                           reply_markup=basicMarkup)
                else:
                    await get_card_from_promo(message, data[0])
                    cur.execute("INSERT INTO users_promos VALUES (?, ?)", (message.from_user.id, message.text))
                    con.commit()
                    if data[1] == 1:
                        cur.execute(f'DELETE FROM promos WHERE promo = "{message.text}"')
                        con.commit()
                    else:
                        cur.execute(f'UPDATE promos SET times = times - 1 WHERE promo = "{message.text}"')
                        con.commit()
            else:
                await bot.send_message(message.chat.id, 'Такого промокода мы не добавляли 🥶', reply_markup=basicMarkup)
            '''cur.execute(f'SELECT promo FROM users_promos WHERE user_id = {message.from_user.id}')
            data = cur.fetchall()
            repeat = False
            if data != None:
                for el in data:
                    if el == message.text:
                        repeat = True
            if repeat != False:
                await bot.send_message(message.chat.id, 'Ты уже использовал данный промокод! 🤕', reply_markup=basicMarkup)'''
            '''else:
                cur.execute(f'SELECT card_id, times FROM promos WHERE promo = "{message.text}"')
                data = cur.fetchone()
                if data != None:
                    await get_card_from_promo(message, data[0])
                    cur.execute("INSERT INTO users_promos VALUES (?, ?)", (message.from_user.id, message.text))
                    con.commit()
                    if data[1] == 1:
                        cur.execute(f'DELETE FROM promos WHERE promo = "{message.text}"')
                        con.commit()
                    else:
                        cur.execute(f'UPDATE promos SET times = times - 1 WHERE promo = "{message.text}"')
                        con.commit()
                else:
                    await bot.send_message(message.chat.id, 'Такого промокода мы не добавляли 🥶', reply_markup=basicMarkup)'''
            storage[str(message.chat.id)] = 'init'
            storage.close()
    else:
        await bot.send_message(message.chat.id, f'❌ Вы были забанены!')
    cur.close()
    con.close()


if __name__ == "__main__":
    '''season_thread = threading.Thread(target=season_update)
    season_thread.start()
    push_thread = threading.Thread(target=push_update)
    push_thread.start()'''
    #loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(push_update())
    loop.create_task(alert_update())
    loop.create_task(season_update())
    loop.create_task(pass_update())
    loop.create_task(check_update())
    executor.start_polling(dp, skip_updates=True)