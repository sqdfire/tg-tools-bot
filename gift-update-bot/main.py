import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import json

# Конфигурация
BOT_TOKEN = "#"  # Укажи свой токен
STAR_GIFTS_FILE = "../venv/star_gifts.json"
TARGET_CHANNEL = "#" #Канал с которого берем уведомления

# Конвертация TON в звезды
STARS_PER_TON = 48.72  # Количество звезд за 1 TON

# Загрузка списка подписчиков
SUBSCRIBERS_FILE = "subscribers.json"
try:
    with open(SUBSCRIBERS_FILE, "r") as f:
        subscribers = json.load(f)
except FileNotFoundError:
    subscribers = {}

bot = telebot.TeleBot(BOT_TOKEN)


# Сохранение списка подписчиков
def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f)

def load_gifts():
    try:
        with open(STAR_GIFTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)  # Загружаем НОВЫЕ данные
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("📋 Последние подарки"))
    keyboard.row(KeyboardButton("🔔 Подписаться"), KeyboardButton("🔕 Отписаться"))
    keyboard.row(KeyboardButton("📐 TON в звезды"), KeyboardButton("⭐️ Звезды в TON"))

    bot.send_message(message.chat.id, "Привет! Я бот уведомлений о новых NFT подарках.\n\nИспользуй кнопки ниже:",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in ["📋 Последние подарки", "🔔 Подписаться", "🔕 Отписаться",
                                                           "📐 TON в звезды", "⭐️ Звезды в TON"])
def handle_buttons(message):
    user_id = str(message.from_user.id)

    if message.text == "📋 Последние подарки":
        from datetime import datetime
        gifts = load_gifts()
        total_gifts = len(gifts)
        today = datetime.now().strftime('%Y-%m-%d')
        bot.send_message(
            message.chat.id,
            f"Всего подарков на {today}: {total_gifts}🎁"
        )

    elif message.text == "🔔 Подписаться":
        if subscribers.get(user_id):  # Проверяем подписку
            bot.send_message(message.chat.id, "💡Вы уже подписаны на уведомления!")
        else:
            subscribers[user_id] = True
            save_subscribers()
            bot.send_message(message.chat.id, "✅ Вы подписаны на уведомления!")

    elif message.text == "🔕 Отписаться":
        if subscribers.pop(user_id, None):  # Если был подписан, удаляем
            save_subscribers()
            bot.send_message(message.chat.id, "❌ Вы отписались от уведомлений!")
        else:
            bot.send_message(message.chat.id, "⚠️ Вы не были подписаны.")

    elif message.text == "📐 TON в звезды":
        bot.send_message(message.chat.id, "Введите количество TON для конвертации:")
        bot.register_next_step_handler(message, ton_conversion_handler)  # Ждём ввод

    elif message.text == "⭐️ Звезды в TON":
        bot.send_message(message.chat.id, "Введите количество звёзд для конвертации:")
        bot.register_next_step_handler(message, stars_conversion_handler)  # Ждём ввод


# Конвертация TON в звезды
def ton_conversion_handler(message):
    try:
        ton_amount = float(message.text)
        stars_per_ton = ton_amount * STARS_PER_TON
        bot.send_message(message.chat.id, f"💎 {ton_amount} TON ≈ {stars_per_ton:.2f} ⭐")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число.")


# Конвертация звезд в TON
def stars_conversion_handler(message):
    try:
        stars_amount = float(message.text)
        ton_amount = stars_amount / STARS_PER_TON
        bot.send_message(message.chat.id, f"⭐ {stars_amount} ≈ {ton_amount:.4f} TON 💎")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число.")


# Проверка сообщений в канале
@bot.channel_post_handler(func=lambda message: True)
def monitor_channel(message):
    if "new limited gift" in message.text.lower():
        for user_id in subscribers.keys():
            try:
                bot.send_message(int(user_id), f"🚀 Новые NFT подарки доступны!\n{message.text}")
            except Exception as e:
                print(f"Ошибка отправки {user_id}: {e}")


print("✅ Бот запущен!")
bot.polling(none_stop=True)