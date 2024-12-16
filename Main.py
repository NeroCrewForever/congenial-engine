import asyncio
import random
import logging
import sqlite3
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from datetime import datetime
from quests_data import blade_quests  # Импорт квестов


# Замените на токен своего бота
TOKEN = "7113693174:AAF85CBzP6DLVpA7A858zA9M3mfiC_D7Kv0"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Словарь с карточками, их редкостью и URL фото
cards = {
    "Химеко": (
        "common",
        "https://static.wikia.nocookie.net/narutofanon/images/a/a5/GA_-_Uzumakisen_-_Pro.jpeg/revision/latest?cb=20230510000039"),
    "Зеле": (
        "common", "https://avatars.mds.yandex.net/i?id=149080c1a369a4ecbefc26eb2716c219_l-12316895-images-thumbs&n=13"),
    "Ханья": (
        "common", "https://i.pinimg.com/736x/10/96/c1/1096c1e592ee676a6e8bc1c4cc93bc0b.jpg"),
    "Зарянка": (
        "mythical", "https://cs13.pikabu.ru/post_img/2024/05/27/10/og_og_1716826129287938874.jpg"),
    "Блейд": (
        "mythical",
        "https://sun9-76.userapi.com/impg/6PwAT_exDdVGUUm6dshtgAT37oRBPtkAS614RA/D4JuH2SN2iw.jpg?size=1280x791&quality=95&sign=6047b7d395a4b30bb0ac2361dd9a6b58&c_uniq_tag=472Q78q2i_iYs3CqZ8YtNU_iKvbkcmoOU-wp2v5wl5A&type=album"),
    "Ахерон": (
        "legendary",
        "https://newcdn.igromania.ru/articles/pics/tmp/images/2024/5/2/86b83d2b-de1d-4130-a8d6-100b6180c9ab.webp"),
}

rarity_weights = {
    "common": 70,
    "mythical": 25,
    "legendary": 5
}

rarity_scores = {
    "common": 1000,
    "mythical": 5000,
    "legendary": 10000
}

# Базовое время кулдауна
base_cooldown = 250
base_upgrade_cost = 250

# Подключение к базе данных
DATABASE_NAME = "users.db"

user_messages = {}
user_quests = {}
base_quest_points = 10000


async def create_table():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER,
                upgrade_level INTEGER,
                last_card_time TEXT,
                upgrade_cost INTEGER,
                last_card_time_db TEXT,
                characters TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при создании таблицы: {e}")
        raise


async def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        data = cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении данных пользователя: {e}")
        conn.close()
        return {"points": 0, "upgrade_level": 0, "last_card_time": None, "cooldown": base_cooldown,
                "upgrade_cost": base_upgrade_cost, "last_card_time_db": None, "characters": []}
    finally:
        conn.close()
    if data:
        try:
            last_card_time = datetime.fromisoformat(data[3]) if data[3] else None
            last_card_time_db = datetime.fromisoformat(data[5]) if data[5] else None
            characters = data[6].split(",") if data[6] else []
        except ValueError as e:
            logging.error(f"Ошибка при парсинге даты: {e}, raw data = {data[3]}")
            last_card_time = None
            last_card_time_db = None
            characters = []
        return {
            "points": data[1],
            "upgrade_level": data[2],
            "last_card_time": last_card_time,
            "cooldown": base_cooldown - data[2],
            "upgrade_cost": data[4],
            "last_card_time_db": last_card_time_db,
            "characters": characters
        }
    else:
        return {"points": 0, "upgrade_level": 0, "last_card_time": None, "cooldown": base_cooldown,
                "upgrade_cost": base_upgrade_cost, "last_card_time_db": None, "characters": []}


async def save_user_data(user_id, points, upgrade_level, last_card_time, upgrade_cost, last_card_time_db, characters):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, points, upgrade_level, last_card_time, upgrade_cost, last_card_time_db, characters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, points, upgrade_level, last_card_time.isoformat() if last_card_time else None, upgrade_cost,
              last_card_time_db.isoformat() if last_card_time_db else None, ",".join(characters)))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении данных пользователя: {e}")
    finally:
        conn.close()


# Функция для получения карточки случайной редкости с учетом весов
def get_random_card():
    rarities = list(rarity_weights.keys())
    weights = list(rarity_weights.values())
    rarity = random.choices(rarities, weights=weights, k=1)[0]
    available_cards = [card for card, (card_rarity, _) in cards.items() if card_rarity == rarity]
    card_name = random.choice(available_cards)
    _, photo_url = cards[card_name]
    return card_name, rarity, photo_url


async def send_or_edit_message(chat_id, text, reply_markup=None, photo=None, parse_mode="HTML"):
    user_id = chat_id
    if user_id in user_messages and user_messages[user_id]:
        try:
            if photo:
                await bot.edit_message_media(chat_id=chat_id, message_id=user_messages[user_id],
                                             media=types.InputMediaPhoto(media=photo, caption=text,
                                                                         parse_mode=parse_mode),
                                             reply_markup=reply_markup)
            else:
                await bot.edit_message_text(chat_id=chat_id, message_id=user_messages[user_id], text=text,
                                            parse_mode=parse_mode, reply_markup=reply_markup)
            return user_messages[user_id]
        except Exception as e:
            logging.error(f"Ошибка при редактировании сообщения: {e}")
            pass  # Продолжаем и отправляем новое сообщение, если редактирование не удалось.

    if photo:
        message = await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode=parse_mode,
                                       reply_markup=reply_markup)
    else:
        message = await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)

    user_messages[user_id] = message.message_id
    return message.message_id


# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбить карту", callback_data="card"),
         InlineKeyboardButton(text="Прокачать", callback_data="upgrade")],
        [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
         InlineKeyboardButton(text="Статистика", callback_data="stats")]
    ])
    await send_or_edit_message(chat_id=user_id, text="Привет! Выбери действие:", reply_markup=keyboard)


# Обработчик команды /card
@router.callback_query(F.data == "card")
async def card_command(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = await get_user_data(user_id)

    last_card_time_db = user_data["last_card_time_db"]
    cooldown = user_data["cooldown"]

    if last_card_time_db and (time.time() - last_card_time_db.timestamp()) < cooldown:
        remaining_time = int(cooldown - (time.time() - last_card_time_db.timestamp()))
        await query.answer(f"Подожди еще {remaining_time} секунд, прежде чем использовать /card снова.",
                           show_alert=True)
        return

    card_name, rarity, photo_url = get_random_card()
    points = rarity_scores[rarity]

    user_data["points"] += points
    user_data["last_card_time_db"] = datetime.now()

    is_new_card = card_name not in user_data["characters"]
    if is_new_card:
        user_data["characters"].append(card_name)

    await save_user_data(user_id, user_data["points"], user_data["upgrade_level"], user_data["last_card_time"],
                         user_data["upgrade_cost"], user_data["last_card_time_db"], user_data["characters"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбить карту", callback_data="card"),
         InlineKeyboardButton(text="Прокачать", callback_data="upgrade")],
        [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
         InlineKeyboardButton(text="Статистика", callback_data="stats")]
    ])

    description = f"""
       {'🚀 Новая карточка — ' if is_new_card else '🔂 Повторная карточка — '}«{card_name}»
💎 Редкость • {rarity.capitalize()}
✨ Очки • +{points:,} 
       """

    await send_or_edit_message(chat_id=query.message.chat.id, photo=URLInputFile(photo_url),
                               text=description.replace(" ", " ").replace("!", r"\!").replace("+", r"\+"),
                               parse_mode="MarkdownV2",
                               reply_markup=keyboard)


# Обработчик команды /upgrade
@router.callback_query(F.data == "upgrade")
async def upgrade_command(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = await get_user_data(user_id)
    points = user_data["points"]
    upgrade_cost = user_data["upgrade_cost"]

    if points < upgrade_cost:
        await query.answer(f"Недостаточно очков. Нужно {upgrade_cost:,} очков.", show_alert=True)
        return

    user_data["points"] -= upgrade_cost
    user_data["upgrade_level"] += 1
    user_data["upgrade_cost"] = int(upgrade_cost * 1.2)

    # Обновляем кулдаун
    user_data["cooldown"] = base_cooldown - user_data["upgrade_level"]

    await save_user_data(user_id, user_data["points"], user_data["upgrade_level"], user_data["last_card_time"],
                         user_data["upgrade_cost"], user_data["last_card_time_db"], user_data["characters"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбить карту", callback_data="card"),
         InlineKeyboardButton(text="Прокачать", callback_data="upgrade")],
        [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
         InlineKeyboardButton(text="Статистика", callback_data="stats")]
    ])

    text = (
        f"Улучшение!\n\n"
        f"Кулдаун уменьшен на 1 секунду. Теперь кулдаун: {user_data['cooldown']:.1f} секунд.\n"
        f"Стоимость следующего улучшения: {user_data['upgrade_cost']:,} очков.\n"
        f"У вас осталось {user_data['points']:,} очков."
    )

    await send_or_edit_message(chat_id=query.message.chat.id, text=text,
                               reply_markup=keyboard, parse_mode="HTML")

    await query.answer()


# Обработчик команды /stats
@router.callback_query(F.data == "stats")
async def stats_command(query: types.CallbackQuery):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при запросе статистики: {e}")
        users = []
    finally:
        conn.close()

    if not users:
        await send_or_edit_message(chat_id=query.message.chat.id, text="Пока нет пользователей.", parse_mode="HTML")
        return

    stats_text = "<b>📊 Статистика пользователей 📊</b>\n\n"
    for user in users:
        user_id, points, upgrade_level, _, upgrade_cost, _, characters = user
        user_info = await bot.get_chat(user_id)
        username = user_info.username or user_info.first_name
        stats_text += f"<b>{username}</b>: {points:,} очков, Уровень: {upgrade_level}, Стоимость улучшения: {upgrade_cost:,}, Выбито персонажей: {len(characters.split(',')) if characters else 0}/{len(cards)}\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбить карту", callback_data="card"),
         InlineKeyboardButton(text="Прокачать", callback_data="upgrade")],
        [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
         InlineKeyboardButton(text="Статистика", callback_data="stats")]
    ])

    await send_or_edit_message(chat_id=query.message.chat.id, text=stats_text, parse_mode="HTML", reply_markup=keyboard)
    await query.answer()


# Обработчик команды /mychars
@router.callback_query(F.data == "mychars")
async def mychars_command(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = await get_user_data(user_id)
    characters = user_data["characters"]
    if not characters:
        await send_or_edit_message(chat_id=query.message.chat.id, text="Вы пока не выбили ни одного персонажа.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for char in characters:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=char, callback_data=f"quests_{char}")])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Выбить карту", callback_data="card"),
        InlineKeyboardButton(text="Прокачать", callback_data="upgrade")
    ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
        InlineKeyboardButton(text="Статистика", callback_data="stats")
    ])

    await send_or_edit_message(chat_id=query.message.chat.id, text="Выберите персонажа:", reply_markup=keyboard,
                               parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data.startswith("quests_"))
async def show_character_quests(query: types.CallbackQuery):
    user_id = query.from_user.id
    char_name = query.data.split("_")[1]

    if char_name == "Блейд":
        await start_quest(query, user_id, "start", blade_quests)
    else:
        await send_or_edit_message(chat_id=query.message.chat.id, text=f"Квесты для {char_name} в разработке.",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars")]]))


async def start_quest(query: types.CallbackQuery, user_id, quest_key, quest_data):
    user_quests[user_id] = {"current_quest": quest_key, "quest_data": quest_data}
    await show_quest_step(query, user_id)


async def show_quest_step(query: types.CallbackQuery, user_id):
    current_quest = user_quests[user_id]["current_quest"]
    quest_data = user_quests[user_id]["quest_data"]

    if current_quest == "end":
        user_data = await get_user_data(user_id)
        user_data["points"] += base_quest_points
        await save_user_data(user_id, user_data["points"], user_data["upgrade_level"], user_data["last_card_time"],
                             user_data["upgrade_cost"], user_data["last_card_time_db"], user_data["characters"])

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выбить карту", callback_data="card"),
             InlineKeyboardButton(text="Прокачать", callback_data="upgrade")],
            [InlineKeyboardButton(text="Мои персонажи", callback_data="mychars"),
             InlineKeyboardButton(text="Статистика", callback_data="stats")]
        ])

        await send_or_edit_message(chat_id=query.message.chat.id,
                                   text=f"Вы завершили квест и получили {base_quest_points:,} очков!",
                                   reply_markup=keyboard)
        return

    step = quest_data.get(current_quest)
    if not step:
        await send_or_edit_message(chat_id=query.message.chat.id, text="Ошибка квеста")
        return

    text = step["text"]
    image = step.get("image")
    options = step["options"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option_text, callback_data=option_callback) for option_text, option_callback in
         options]
    ])

    await send_or_edit_message(chat_id=query.message.chat.id, text=text, photo=URLInputFile(image) if image else None,
                               reply_markup=keyboard)


@router.callback_query(F.data.startswith("blade_"))
async def handle_blade_quest(query: types.CallbackQuery):
    user_id = query.from_user.id
    option_callback = query.data
    if user_id not in user_quests:
        await send_or_edit_message(chat_id=query.message.chat.id, text="Ошибка, начните квест заново")
        return

    user_quests[user_id]["current_quest"] = option_callback
    await show_quest_step(query, user_id)


# Запуск бота
async def main():
    await create_table()
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())