import os
import sqlite3
import logging
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultGame
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler
)

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot_errors.log',
    filemode='a'
)
logger = logging.getLogger(__name__)


# Инициализация БД
def init_db():
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                score INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Exception as e:
        logger.error(f"DB Error: {e}", exc_info=True)
    finally:
        conn.close()


init_db()

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_text(
            "🐍 Змейка 2.0\n"
            "Команды:\n"
            "/play - Играть\n"
            "/top - Топ игроков\n"
            "/help - Помощь"
        )
    except Exception as e:
        logger.error(f"Start error: {e}", exc_info=True)


async def play(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_game(game_short_name="snake_game")
        logger.info(f"User {update.effective_user.id} started game")
    except Exception as e:
        logger.error(f"Play error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка запуска игры")


async def top_players(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, MAX(score) as max_score 
            FROM scores 
            GROUP BY user_id 
            ORDER BY max_score DESC 
            LIMIT 10
        ''')
        results = cursor.fetchall()

        if not results:
            await update.message.reply_text("🏆 Рейтинг пуст!")
            return

        response = "🏆 Топ игроков:\n"
        for i, (username, score) in enumerate(results, 1):
            response += f"{i}. {username}: {score}\n"

        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Top players error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки рейтинга")
    finally:
        conn.close()


async def game_callback(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()

        if query.game_short_name == "snake_game" and hasattr(query, 'game_score'):
            save_score(
                query.from_user.id,
                query.from_user.username or query.from_user.first_name,
                query.game_score
            )
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)


def save_score(user_id: int, username: str, score: int):
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scores (user_id, username, score)
            VALUES (?, ?, ?)
        ''', (user_id, username, score))
        conn.commit()
    except Exception as e:
        logger.error(f"Save score error: {e}", exc_info=True)
    finally:
        conn.close()


def main():
    if not TOKEN:
        logger.critical("Token not found! Check .env file")
        return

    try:
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("play", play))
        app.add_handler(CommandHandler("top", top_players))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CallbackQueryHandler(game_callback))

        logger.info("Bot started successfully")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()