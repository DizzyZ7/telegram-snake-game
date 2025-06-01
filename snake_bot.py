import os
import sqlite3
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot_errors.log'
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def init_db():
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = f"@{user.username}" if user.username else user.first_name
    await update.message.reply_text(
        f"🐍 Привет, {name}!\n\n"
        "🔹 /play — Запустить игру\n"
        "🏆 /top — Топ игроков\n"
        "✨ /mytop — Мои рекорды\n"
        "🕒 /last — Последние игры",
        parse_mode='HTML'
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            "🎮 Запускаем змейку!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="▶ Играть",
                    web_app=WebAppInfo(url="http://localhost:5000/")
                )
            ]])
        )
    except Exception as e:
        logger.error(f"Ошибка запуска игры: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Не удалось запустить игру.")

async def top_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, MAX(score) as best
        FROM scores
        GROUP BY user_id
        ORDER BY best DESC
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("🏆 Пока нет данных.")
        return

    text = "🏆 <b>Топ игроков:</b>\n\n"
    for i, (username, score) in enumerate(rows):
        text += f"{i + 1}. {username}: {score}\n"

    await update.message.reply_text(text, parse_mode='HTML')

async def my_top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT score, strftime('%d.%m.%Y', timestamp)
        FROM scores
        WHERE user_id = ?
        ORDER BY score DESC
        LIMIT 5
    ''', (update.effective_user.id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("📉 У вас пока нет результатов.")
        return

    text = "✨ <b>Ваши рекорды:</b>\n\n"
    for i, (score, date) in enumerate(rows):
        text += f"{i + 1}. {score} очков ({date})\n"

    await update.message.reply_text(text, parse_mode='HTML')

async def last_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, score, strftime('%d.%m.%Y %H:%M', timestamp)
        FROM scores
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("⏱ Пока никто не играл.")
        return

    text = "🕒 <b>Последние игры:</b>\n\n"
    for username, score, time in rows:
        text += f"• {username}: {score} ({time})\n"

    await update.message.reply_text(text, parse_mode='HTML')

def main():
    if not TOKEN:
        logger.critical("❌ Токен не найден! Проверь .env")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("top", top_players))
    app.add_handler(CommandHandler("mytop", my_top))
    app.add_handler(CommandHandler("last", last_games))

    logger.info("✅ Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
