import os
import pytz  # Явно импортируем pytz для работы с часовыми поясами
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("🐍 Нажми /play чтобы начать игру!")


async def play(update: Update, context: CallbackContext) -> None:
    await update.message.reply_game(game_short_name="snake_game")


async def game_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="🐍 Игра загружается...")


def main() -> None:
    # Явно указываем часовой пояс
    application = Application.builder() \
        .token(TOKEN) \
        .arbitrary_callback_data(True) \
        .build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CallbackQueryHandler(game_handler, pattern="^snake_game$"))

    application.run_polling()


if __name__ == "__main__":
    main()