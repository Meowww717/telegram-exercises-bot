from affirmations import EVENING_AFFIRMATIONS, MORNING_AFFIRMATIONS
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import datetime
import random
from pathlib import Path
import os
import json
from dotenv import load_dotenv
load_dotenv()


# CONFIG
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

DATA_FILE = Path("videos.json")

CATEGORIES = [
    "neck",
    "back",
    "shoulders",
    "hips",
    "elbows",
    "knees",
    "ankles & feet",
    "full_body",
    "stretching",
    "face",
]

CATEGORY_LABELS = {
    "neck": "🦒 Neck",
    "back": "🦴 Back",
    "shoulders": "🤷‍♀️ Shoulders",
    "hips": "🦵 Hips",
    "elbows": "💪 Elbows",
    "knees": "🦿 Knees",
    "ankles & feet": "👣 Ankles And Feet",
    "full_body": "🏃 Full body",
    "stretching": "🧘 Stretching",
    "face": "🙂 Face"
}


async def morning_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data["chat_id"]
    affirmation = random.choice(MORNING_AFFIRMATIONS)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🌅 Добрий ранок 💙 / Good morning 💙\n\n"
            f"🇺🇦 {affirmation['ua']}\n\n"
            f"🇬🇧 {affirmation['en']}\n\n"
            "Навіть 5 хвилин руху мають значення.\n"
            "Even 5 minutes of movement count."
        )
    )


async def evening_reminder_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data["chat_id"]
    affirmation = random.choice(EVENING_AFFIRMATIONS)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🌙 Вечірній момент для себе 🤍 / Evening check-in 🤍\n\n"
            f"🇺🇦 {affirmation['ua']}\n\n"
            f"🇬🇧 {affirmation['en']}\n\n"
            "Можна видихнути. День завершено."
        )
    )


async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data["chat_id"]
    affirmation = random.choice(AFFIRMATIONS)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "⏰ Good morning 💙\n\n"
            f"{affirmation}\n\n"
            "Even 5 minutes of movement count."
        )
    )


# STORAGE
def load_data():
    if not DATA_FILE.exists():
        return {cat: [] for cat in CATEGORIES}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# KEYBOARDS
def categories_keyboard():
    rows = []
    row = []

    for cat in CATEGORIES:
        row.append(InlineKeyboardButton(
            CATEGORY_LABELS[cat], callback_data=f"cat:{cat}"))
        if len(row) == 3:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return InlineKeyboardMarkup(rows)


def category_actions_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add video", callback_data="add"),
            InlineKeyboardButton("🗑 Delete video", callback_data="delete"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="back")
        ]
    ])


# COMMANDS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # remove old jobs
    for job in context.job_queue.get_jobs_by_name(f"morning_{chat_id}"):
        job.schedule_removal()
    for job in context.job_queue.get_jobs_by_name(f"evening_{chat_id}"):
        job.schedule_removal()

    # morning 08:00
    context.job_queue.run_daily(
        morning_reminder_job,
        time=datetime.time(hour=8, minute=0),
        data={"chat_id": chat_id},
        name=f"morning_{chat_id}"
    )

    # evening 21:00
    context.job_queue.run_daily(
        evening_reminder_job,
        time=datetime.time(hour=21, minute=0),
        data={"chat_id": chat_id},
        name=f"evening_{chat_id}"
    )

    await update.message.reply_text(
        "💙 Daily reminders set:\n"
        "🌅 Morning — 08:00\n"
        "🌙 Evening — 21:00"
    )

    await update.message.reply_text(
        "💪 Choose a category to do exercises now:",
        reply_markup=categories_keyboard()
    )


# CALLBACKS
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # category selected
    if data.startswith("cat:"):
        category = data.split(":")[1]
        context.user_data["category"] = category
        await show_category(query, category)

    # add video
    elif data == "add":
        category = context.user_data.get("category")
        if not category:
            await query.message.reply_text("❌ Choose category first")
            return

        context.user_data["action"] = "add"
        await query.message.reply_text(
            f"📎 Send me the video link for *{category}*",
            parse_mode="Markdown"
        )

    # delete video
    elif data == "delete":
        await show_delete_options(query, context)

    # delete конкретне
    elif data.startswith("del:"):
        index = int(data.split(":")[1])
        await delete_video(query, context, index)

    # back
    elif data == "back":
        context.user_data.clear()
        await query.message.reply_text(
            "💪 Choose a category:",
            reply_markup=categories_keyboard()
        )


# ACTIONS
async def show_category(query, category):
    data = load_data()
    videos = data.get(category, [])

    text = f"💪 *{category.upper()}*\n\n"

    if not videos:
        text += "No videos yet."
    else:
        for i, url in enumerate(videos, 1):
            text += f"{i}. {url}\n"

    await query.message.reply_text(
        text,
        reply_markup=category_actions_keyboard(),
        parse_mode="Markdown"
    )


async def show_delete_options(query, context):
    category = context.user_data.get("category")
    if not category:
        await query.message.reply_text("❌ Choose category first")
        return

    data = load_data()
    videos = data.get(category, [])

    if not videos:
        await query.message.reply_text("📭 No videos to delete")
        return

    keyboard = []

    for i in range(len(videos)):
        keyboard.append([
            InlineKeyboardButton(
                f"❌ Delete {i + 1}",
                callback_data=f"del:{i}"
            )
        ])

    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back")])

    await query.message.reply_text(
        "🗑 Select video to delete:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def delete_video(query, context, index):
    category = context.user_data.get("category")
    data = load_data()

    try:
        removed = data[category].pop(index)
        save_data(data)
        await query.message.reply_text(f"🗑 Removed:\n{removed}")
    except Exception:
        await query.message.reply_text("❌ Failed to delete")

    await show_category(query, category)


# MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("action") == "add":
        category = context.user_data.get("category")
        url = update.message.text.strip()

        data = load_data()
        data[category].append(url)
        save_data(data)

        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Added to *{category}*",
            parse_mode="Markdown"
        )

        await update.message.reply_text(
            "💪 Choose a category:",
            reply_markup=categories_keyboard()
        )


# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
