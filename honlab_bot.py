import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в Railway!")

BRAND_NAME = "HONLAB — Точность за 3 часа"

STANDARD_SERVICES = {
    "block_honing": {"name": "Расточка блока", "price": 3000},
    "cylinder_sleeving": {"name": "Гильзовка", "price": 4500},
    "head_milling": {"name": "Фрезеровка ГБЦ", "price": 2000},
    "crankshaft_measurement": {"name": "Замер коленвала", "price": 0}
}
EXPRESS_MULT = 1.3
BONUS = ["crankshaft_measurement"]

(SELECT_SERVICE, SELECT_TIME_SLOT, CONTACT_INFO) = range(3)

def init_db():
    conn = sqlite3.connect('honlab.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (telegram_id INTEGER UNIQUE)''')
    conn.commit()
    conn.close()

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱️ Записаться", callback_data='booking')],
        [InlineKeyboardButton("🧮 Калькулятор", callback_data='calc')],
        [InlineKeyboardButton("📱 Контакты", callback_data='contacts')]
    ])

async def start(update: Update, context):
    init_db()
    await update.message.reply_text(
        f"🚀 <b>{BRAND_NAME}</b>\n\n"
        "🔥 Расточка, гильзовка, хонингование — идеальная геометрия двигателя за один визит!\n\n"
        "✅ Бесплатный замер коленвала\n"
        "✅ Гарантия 1 год",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def menu_handler(update, context):
    q = update.callback_query
    await q.answer()
    if q.data == 'booking':
        context.user_data['order'] = {'services': [], 'is_express': False}
        await q.edit_message_text(
            "⚡ Экспресс (+30%) или ⏱️ Стандарт?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Экспресс", callback_data='expr')],
                [InlineKeyboardButton("⏱️ Стандарт", callback_data='std')]
            ])
        )
        return SELECT_SERVICE
    elif q.data == 'calc':
        # Упрощённый калькулятор
        text = (
            "<b>🧮 Цены:</b>\n"
            "• Расточка блока — 3000 ₽\n"
            "• Гильзовка — 4500 ₽\n"
            "• Фрезеровка ГБЦ — 2000 ₽\n"
            "• Замер коленвала — бесплатно\n\n"
            "<b>Экспресс (+30%):</b> готовность за 3 часа"
        )
        await q.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='back')]]))
    elif q.data == 'contacts':
        await q.edit_message_text(
            "📍 Великий Новгород\n📞 +7 (911) 629-61-09\n🕗 Понедельник-Пятница 9:00–18:00",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='back')]])
        )
    elif q.data == 'back':
        await q.edit_message_text("🚀 <b>HONLAB</b>", reply_markup=main_menu(), parse_mode="HTML")
    return ConversationHandler.END

async def simple_reply(update, context):
    await update.message.reply_text("📱 Используйте меню!", reply_markup=main_menu())

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, simple_reply))
    app.run_polling()

if __name__ == "__main__":
    main()
