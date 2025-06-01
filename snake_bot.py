import os
import sqlite3
import logging
from datetime import datetime
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
    filename='bot_errors.log'
)
logger = logging.getLogger(__name__)


# Инициализация БД
def init_db():
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON scores (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON scores (score)')
    conn.commit()
    conn.close()


init_db()

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        username = f"@{user.username}" if user.username else user.first_name
        await update.message.reply_text(
            f"🐍 Привет, {username}!\n\n"
            "🔹 /play - Начать игру\n"
            "🏆 /top - Топ игроков\n"
            "✨ /mytop - Мой рейтинг\n"
            "🕒 /last - Последние игры",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Start error: {e}", exc_info=True)


async def play(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_game(game_short_name="snake_game")
    except Exception as e:
        logger.error(f"Play error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка запуска игры")


async def top_players(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        # Топ-10 всех времен
        cursor.execute('''
            SELECT username, MAX(score) as max_score 
            FROM scores 
            GROUP BY user_id 
            ORDER BY max_score DESC 
            LIMIT 10
        ''')
        top = cursor.fetchall()

        response = "🏆 <b>Топ игроков:</b>\n\n"
        if not top:
            response += "Пока нет результатов"
        else:
            response += "\n".join(
                f"{i + 1}. {name}: {score}"
                for i, (name, score) in enumerate(top)
            )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Top error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки рейтинга")
    finally:
        conn.close()


async def my_top(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT score, strftime('%d.%m.%Y', timestamp) 
            FROM scores 
            WHERE user_id = ? 
            ORDER BY score DESC 
            LIMIT 5
        ''', (update.effective_user.id,))

        scores = cursor.fetchall()

        if not scores:
            await update.message.reply_text("🎮 У вас пока нет результатов!")
            return

        response = (
                "✨ <b>Ваши лучшие результаты:</b>\n\n" +
                "\n".join(
                    f"{i + 1}. {score} ({date})"
                    for i, (score, date) in enumerate(scores)
                )
        )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"MyTop error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки данных")
    finally:
        conn.close()


async def last_games(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, score, strftime('%d.%m.%Y %H:%M', timestamp) 
            FROM scores 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')

        games = cursor.fetchall()

        response = (
                "🕒 <b>Последние игры:</b>\n\n" +
                "\n".join(
                    f"• {username}: {score} ({date})"
                    for username, score, date in games
                )
        )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"LastGames error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки данных")
    finally:
        conn.close()


async def game_callback(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()

        if query.game_short_name == "snake_game" and hasattr(query, 'game_score'):
            user = query.from_user
            username = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name or ''}"

            conn = sqlite3.connect('scores.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores (user_id, username, score)
                VALUES (?, ?, ?)
            ''', (
                user.id,
                username.strip(),
                query.game_score
            ))
            conn.commit()
            logger.info(f"User {user.id} scored {query.game_score}")
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
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
        app.add_handler(CommandHandler("mytop", my_top))
        app.add_handler(CommandHandler("last", last_games))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CallbackQueryHandler(game_callback))

        logger.info("Bot started successfully")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()import os
import sqlite3
import logging
from datetime import datetime
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
    filename='bot_errors.log'
)
logger = logging.getLogger(__name__)


# Инициализация БД
def init_db():
    conn = sqlite3.connect('scores.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON scores (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON scores (score)')
    conn.commit()
    conn.close()


init_db()

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        username = f"@{user.username}" if user.username else user.first_name
        await update.message.reply_text(
            f"🐍 Привет, {username}!\n\n"
            "🔹 /play - Начать игру\n"
            "🏆 /top - Топ игроков\n"
            "✨ /mytop - Мой рейтинг\n"
            "🕒 /last - Последние игры",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Start error: {e}", exc_info=True)


async def play(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_game(game_short_name="snake_game")
    except Exception as e:
        logger.error(f"Play error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка запуска игры")


async def top_players(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        # Топ-10 всех времен
        cursor.execute('''
            SELECT username, MAX(score) as max_score 
            FROM scores 
            GROUP BY user_id 
            ORDER BY max_score DESC 
            LIMIT 10
        ''')
        top = cursor.fetchall()

        response = "🏆 <b>Топ игроков:</b>\n\n"
        if not top:
            response += "Пока нет результатов"
        else:
            response += "\n".join(
                f"{i + 1}. {name}: {score}"
                for i, (name, score) in enumerate(top)
            )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Top error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки рейтинга")
    finally:
        conn.close()


async def my_top(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT score, strftime('%d.%m.%Y', timestamp) 
            FROM scores 
            WHERE user_id = ? 
            ORDER BY score DESC 
            LIMIT 5
        ''', (update.effective_user.id,))

        scores = cursor.fetchall()

        if not scores:
            await update.message.reply_text("🎮 У вас пока нет результатов!")
            return

        response = (
                "✨ <b>Ваши лучшие результаты:</b>\n\n" +
                "\n".join(
                    f"{i + 1}. {score} ({date})"
                    for i, (score, date) in enumerate(scores)
                )
        )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"MyTop error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки данных")
    finally:
        conn.close()


async def last_games(update: Update, context: CallbackContext) -> None:
    try:
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, score, strftime('%d.%m.%Y %H:%M', timestamp) 
            FROM scores 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')

        games = cursor.fetchall()

        response = (
                "🕒 <b>Последние игры:</b>\n\n" +
                "\n".join(
                    f"• {username}: {score} ({date})"
                    for username, score, date in games
                )
        )

        await update.message.reply_text(response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"LastGames error: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки данных")
    finally:
        conn.close()


async def game_callback(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()

        if query.game_short_name == "snake_game" and hasattr(query, 'game_score'):
            user = query.from_user
            username = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name or ''}"

            conn = sqlite3.connect('scores.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores (user_id, username, score)
                VALUES (?, ?, ?)
            ''', (
                user.id,
                username.strip(),
                query.game_score
            ))
            conn.commit()
            logger.info(f"User {user.id} scored {query.game_score}")
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
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
        app.add_handler(CommandHandler("mytop", my_top))
        app.add_handler(CommandHandler("last", last_games))
        app.add_handler(CommandHandler("help", start))
        app.add_handler(CallbackQueryHandler(game_callback))

        logger.info("Bot started successfully")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
