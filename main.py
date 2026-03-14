from flask import Flask
from threading import Thread

app_web = Flask("")


@app_web.route("/")
def home():
    return "Bot is alive"


def run_web():
    app_web.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.start()


import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "8765820951:AAE3cKP8XfGkCtgarui9LhKwgjHnb8Qdj2I"
ADMIN_IDS = [5290445071, 7929629319]

pattern = r'https?://(?:search\.app|share\.google)/[A-Za-z0-9_-]+'

users = {}
user_link_count = {}


def extract_links(text):
    return re.findall(pattern, text)


def extract_links(text):
    return re.findall(pattern, text)


def resolve(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text

    users[user_id] = {"username": user.username, "first_name": user.first_name}

    if user_id not in user_link_count:
        user_link_count[user_id] = 0

    links = extract_links(text)

    if not links:
        await update.message.reply_text("нет ссылок")
        return

    user_link_count[user_id] += len(links)

    result = []

    for link in links:
        final = resolve(link)

        if final not in result:
            result.append(final)

    await update.message.reply_text("\n".join(result),
                                    disable_web_page_preview=True)
    text = update.message.text
    links = extract_links(text)

    if not links:
        await update.message.reply_text("нет ссылок")
        return

    result = []

    for link in links:
        final = resolve(link)
        result.append(final)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    users[user_id] = {"username": user.username, "first_name": user.first_name}

    if user_id not in user_link_count:
        user_link_count[user_id] = 0

    await update.message.reply_text("Привет! 👋\n\n"
                                    "Отправь мне ссылки вида search.app\n"
                                    "и я верну прямые ссылки на статьи.")


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Нет доступа")
        return

    await update.message.reply_text("Админ панель\n\n"
                                    "/users — список пользователей\n"
                                    "/stats — кто сколько ссылок отправил")


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Нет доступа")
        return

    if not users:
        await update.message.reply_text("Пользователей пока нет")
        return

    lines = [f"Пользователей: {len(users)}", ""]

    for uid, data in users.items():
        username = data.get("username") or "-"
        first_name = data.get("first_name") or "-"
        lines.append(f"ID: {uid} | @{username} | {first_name}")

    await update.message.reply_text("\n".join(lines),
                                    disable_web_page_preview=True)


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Нет доступа")
        return

    if not user_link_count:
        await update.message.reply_text("Статистики пока нет")
        return

    lines = ["Статистика по пользователям:", ""]

    for uid, count in user_link_count.items():
        data = users.get(uid, {})
        username = data.get("username") or "-"
        first_name = data.get("first_name") or "-"
        lines.append(
            f"ID: {uid} | @{username} | {first_name} | ссылок: {count}")

    await update.message.reply_text("\n".join(lines),
                                    disable_web_page_preview=True)


telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("admin", admin))
telegram_app.add_handler(CommandHandler("users", admin_users))
telegram_app.add_handler(CommandHandler("stats", admin_stats))
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

keep_alive()

print("FLASK STARTED")
print("TELEGRAM BOT STARTING")

telegram_app.run_polling(
    close_loop=False,
    drop_pending_updates=True
)
