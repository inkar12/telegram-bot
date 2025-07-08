import os
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found in environment variables!")
    exit(1)

# Create bot and Flask app
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
flask_app = Flask(__name__)

# === QUIZ LOGIC ===
questions = [
    {
        "text": "1️⃣ Какой у тебя средний GPA за последние 2 года?",
        "options": ["Ниже 2.5", "2.5–3.3", "3.4–3.8", "3.9–4.0"],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "2️⃣ Как ты оцениваешь свои внеклассные активности (спорт, волонтерство, проекты)?",
        "options": [
            "Пока нет достижений",
            "Есть базовые активности",
            "Хороший уровень участия",
            "Я лидер/создатель в чем-то",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "3️⃣ У тебя есть подтверждённый уровень английского языка?",
        "options": [
            "Нет, вообще",
            "Учусь, но без сертификатов",
            "Готовлюсь к IELTS/TOEFL",
            "Уже есть сертификат",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "4️⃣ Ты знаешь, куда именно хочешь поступать?",
        "options": [
            "Вообще нет",
            "Есть примерные идеи",
            "Выбрал страну и тип вуза",
            "Есть чёткий список вузов",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "5️⃣ Как ты оцениваешь свои шансы на стипендию?",
        "options": [
            "Не верю, что получу",
            "Сомневаюсь, но хочу",
            "Думаю, есть шанс",
            "Уверен(а) в себе",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "6️⃣ Как ты реагируешь, если что-то не получается — например, отказ в поступлении или плохая оценка?",
        "options": [
            "Осмысливаю и строю план камбэка",
            "Сомневаюсь, но продолжаю двигаться",
            "Махаю рукой — всегда есть другой путь",
            "Это сильно задевает, мне нужно время",
        ],
        "scores": [3, 2, 1, 0],
    },
    {
        "text": "7️⃣ Что больше всего мотивирует тебя поступать за границу?",
        "options": [
            "Свобода и независимость",
            "Сделать семью гордой",
            "Построить мощное будущее",
            "Найти себя и понять, кто я",
        ],
        "scores": [2, 1, 3, 2],
    },
    {
        "text": "8️⃣ Что для тебя будет самым важным после окончания учёбы?",
        "options": [
            "Оказывать влияние и менять мир",
            "Зарабатывать хорошо",
            "Жить свободно, без ограничений",
            "Остаться верным(ой) себе",
        ],
        "scores": [3, 2, 1, 2],
    },
]

user_scores = {}
user_steps = {}


# === Bot Handlers ===
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    print(f"📨 Received /start from user {user_id}")
    user_scores[user_id] = 0
    user_steps[user_id] = 0
    send_question(update, context)


def send_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    step = user_steps[user_id]
    q = questions[step]
    markup = ReplyKeyboardMarkup(
        [[o] for o in q["options"]], one_time_keyboard=True, resize_keyboard=True
    )
    context.bot.send_message(chat_id=user_id, text=q["text"], reply_markup=markup)


def answer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    print(f"📨 Received message from user {user_id}: {update.message.text}")

    if user_id not in user_steps:
        context.bot.send_message(
            chat_id=user_id, text="Привет! Отправь /start чтобы начать квиз."
        )
        return

    step = user_steps[user_id]
    q = questions[step]
    if update.message.text not in q["options"]:
        context.bot.send_message(
            chat_id=user_id, text="Пожалуйста, выбери один из предложенных вариантов."
        )
        return

    idx = q["options"].index(update.message.text)
    user_scores[user_id] += q["scores"][idx]
    user_steps[user_id] += 1

    if user_steps[user_id] < len(questions):
        send_question(update, context)
    else:
        score = user_scores[user_id]
        if score <= 8:
            msg = "🟡 Ты — Исследователь.\nТы только в начале пути..."
        elif score <= 16:
            msg = "🟢 Ты — Потенциальный кандидат.\nУ тебя уже есть подходящие идеи..."
        else:
            msg = "🔵 Ты — Готовый аппликант.\nТы собрал всё нужное и готов к подаче..."

        context.bot.send_message(
            chat_id=user_id, text=f"Твой результат: {score}/24\n\n{msg}"
        )
        context.bot.send_message(
            chat_id=user_id, text="🎓 Я поступила в 16 вузов на полный грант..."
        )
        context.bot.send_message(
            chat_id=user_id, text="💡 Напиши результат менеджеру: @speakinkschool"
        )


# === Dispatcher Handlers ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))


# === Webhook Endpoint ===
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200


# Health check (for browser)
@flask_app.route("/")
def home():
    return "<h1>Telegram bot is running on Render!</h1>"


# === Setup Webhook ===
def setup_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.delete_webhook(drop_pending_updates=True)
    bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to {webhook_url}")


# === Run the App ===
if __name__ == "__main__":
    setup_webhook()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
