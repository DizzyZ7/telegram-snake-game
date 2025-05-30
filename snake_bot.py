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

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🐍 Добро пожаловать в Змейку!\n"
        "Используйте команды:\n"
        "/play - Начать игру\n"
        "/help - Помощь"
    )

async def play(update: Update, context: CallbackContext) -> None:
    """Отправка игры по команде /play"""
    try:
        await update.message.reply_game(game_short_name="snake_game")
    except Exception as e:
        await update.message.reply_text(f"🚫 Ошибка: {e}\nПроверьте, зарегистрирована ли игра в @BotFather")

async def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text(
        "🔹 Управление в игре:\n"
        "Стрелки ← ↑ → ↓\n\n"
        "🔹 Команды бота:\n"
        "/play - Начать игру\n"
        "/help - Эта справка"
    )

async def game_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатия на игру"""
    query = update.callback_query
    await query.answer()
    
    # URL вашей игры на GitHub Pages
    game_url = "https://dizzyz7.github.io/telegram-snake-game/snake_game.html"
    
    await query.edit_message_text(
        text=f"🎮 [Нажмите чтобы играть]({game_url})",
        parse_mode='Markdown'
    )

async def inline_query(update: Update, context: CallbackContext) -> None:
    """Обработчик inline-запросов"""
    query = update.inline_query
    if not query:
        return
        
    results = [
        InlineQueryResultGame(
            id="1",
            game_short_name="snake_game",
            reply_markup=None
        )
    ]
    await query.answer(results)

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(game_handler, pattern="^snake_game$"))
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
