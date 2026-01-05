# 🧘‍♀️ Telegram Exercise & Self-Care Bot

A personal Telegram bot for **gentle daily movement, exercise organization, and self-support**.  
Built to help avoid endless saved videos and instead make movement **accessible, structured, and kind**.

---

## ✨ Features

### 💪 Exercise Categories

- Neck
- Back
- Shoulders
- Hips
- Elbows
- Knees
- Ankles & Feet
- Full body
- Stretching
- Face

Each category:

- has its **own image**
- stores a **list of video links**
- supports **add / delete** via buttons

---

### ⏰ Daily Reminders

- 🌅 **Morning reminder (08:00)** with a gentle affirmation
- 🌙 **Evening reminder (21:00)** for grounding and closure
- Uses Telegram `JobQueue`

---

### 💙 Self-Support Affirmations

- Morning & evening affirmations
- Bilingual: **Ukrainian 🇺🇦 + English 🇬🇧**
- Stored separately for clean architecture

---

### 🧩 UX Highlights

- Inline buttons instead of text commands
- Emoji-based category labels
- Category-specific images (no generic “biceps”)
- Calm, non-toxic wellness tone

---

## 🚀 Tech Stack

- Python 3.11
- `python-telegram-bot 20.7`
- JobQueue
- Environment variables for secrets
- Render (24/7 deployment)

---

## 🔐 Environment Variables

The bot requires a Telegram token:
TELEGRAM_BOT_TOKEN=your_bot_token_here

> ⚠️ The token is **never stored in the repository**.

---

## ▶️ Run Locally

```bash
python -m venv venv
source venv/Scripts/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py


☁️ Deployment

The bot is deployed as a 24/7 service on Render:

GitHub-connected

Automatic builds

Environment-based secrets

👩‍💻 Author

Built as a real-life pet project with focus on:

clean structure

usability

emotional sustainability


```
