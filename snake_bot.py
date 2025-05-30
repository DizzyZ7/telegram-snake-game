import os
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultGame
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler
)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден! Проверьте файл .env")


async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🐍 Добро пожаловать в Змейку!\n"
        "Используйте команды:\n"
        "/play - Начать игру\n"
        "/help - Помощь"
    )


async def play(update: Update, context: CallbackContext) -> None:
    """Отправка игры"""
    try:
        await update.message.reply_game(game_short_name="snake_game")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")


async def handle_game(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатия на игру"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎮 Загружаем игру...")


async def inline_query(update: Update, context: CallbackContext) -> None:
    """Inline-режим"""
    await update.inline_query.answer([
        InlineQueryResultGame(
            id="1",
            game_short_name="snake_game"
        )
    ])


def main() -> None:
    """Запуск бота"""
    # Проверка токена перед запуском
    if not TOKEN or len(TOKEN) < 30:
        print("❌ Неверный токен! Проверьте .env файл")
        return

    try:
        application = Application.builder().token(TOKEN).build()

        # Регистрация обработчиков
        handlers = [
            CommandHandler("start", start),
            CommandHandler("play", play),
            CommandHandler("help", start),
            CallbackQueryHandler(handle_game, pattern="^snake_game$"),
            InlineQueryHandler(inline_query)
        ]

        for handler in handlers:
            application.add_handler(handler)

        print("🤖 Бот запущен!")
        application.run_polling()

    except Exception as e:
        print(f"🚨 Ошибка при запуске: {str(e)}")


if __name__ == "__main__":
    print("🔄 Запуск бота...")
    main()