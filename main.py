import os
import logging
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Flask сервер для Render ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "✅ Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)


# --- Telegram Bot ---
TOKEN = os.getenv("BOT_TOKEN")  # Токен в Render → Environment
CHANNEL_ID = -1002208073820     # замени на свой канал
ADMIN_ID = 1781318354           # замени на свой ID

participants = set()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_menu(user_id):
    buttons = [[InlineKeyboardButton("✅ Участвовать", callback_data="join")]]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton("📋 Список участников", callback_data="list")])
        buttons.append([InlineKeyboardButton("🎲 Выбрать победителя", callback_data="winner")])
        buttons.append([InlineKeyboardButton("🔄 Сброс участников", callback_data="reset")])
        buttons.append([InlineKeyboardButton("📢 Отправить кнопку в канал", callback_data="send_button")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Меню:", reply_markup=get_main_menu(update.effective_user.id))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.full_name

    if query.data == "join":
        participants.add(username)
        await query.edit_message_text("Ты участвуешь! 🎉", reply_markup=get_main_menu(user_id))

    elif query.data == "list" and user_id == ADMIN_ID:
        text = "📋 Участники:\n" + "\n".join(participants) if participants else "❌ Участников пока нет."
        await query.edit_message_text(text, reply_markup=get_main_menu(user_id))

    elif query.data == "winner" and user_id == ADMIN_ID:
        text = f"🎉 Победитель: {random.choice(list(participants))}" if participants else "❌ Нет участников."
        await query.edit_message_text(text, reply_markup=get_main_menu(user_id))

    elif query.data == "reset" and user_id == ADMIN_ID:
        participants.clear()
        await query.edit_message_text("🔄 Участники сброшены.", reply_markup=get_main_menu(user_id))

    elif query.data == "send_button" and user_id == ADMIN_ID:
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Участвовать", callback_data="join")]])
        await context.bot.send_message(chat_id=CHANNEL_ID, text="🚀 Розыгрыш открыт! Жмите кнопку ниже:", reply_markup=join_button)
        await query.edit_message_text("Кнопка отправлена в канал 📢", reply_markup=get_main_menu(user_id))

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
