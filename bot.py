import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found in environment variables!")
    exit(1)

# Create bot and updater
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Flask app for webhooks
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
        [[o] for o in q["options"]],
        one_time_keyboard=True,
        resize_keyboard=True
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
            msg = (
                "🟡 Ты — Исследователь.\n"
                "Ты только в начале пути и тебе важно разобраться в возможностях, требованиях и стратегиях.\n"
                "Но это уже отличное начало!"
            )
        elif score <= 16:
            msg = (
                "🟢 Ты — Потенциальный кандидат.\n"
                "У тебя уже есть подходящие идеи и навыки. "
                "Немного усилий — и ты сможешь собрать сильное портфолио и выиграть грант."
            )
        else:
            msg = (
                "🔵 Ты — Готовый аппликант.\n"
                "Ты собрал всё нужное и готов к подаче. С правильной стратегией у тебя отличные шансы попасть в топ-вуз!"
            )

        context.bot.send_message(chat_id=user_id, text=f"Твой результат: {score}/24\n\n{msg}")

        context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎓 Я поступила в 16 вузов на полный грант и сейчас учусь в топовом liberal arts college в США.\n\n"
                "🔸 Первый раз — поступила туда, куда не хотела\n"
                "🔸 Второй — сильно старалась, но всё ещё не идеально\n"
                "🔸 Третий — правильная стратегия, правильный результат\n\n"
                "📌 У тебя тоже получится!"
            ),
        )

        context.bot.send_message(
            chat_id=user_id,
            text="💡 Хочешь бесплатную стратегию? Напиши результат менеджеру: @speakinkschool"
        )

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

# === Flask Routes ===
@flask_app.route('/')
def health_check():
    print("📍 / (root) endpoint accessed")
    return """
    <h1>Telegram Bot is Running</h1>
    <p><a href='/test'>Test Route</a></p>
    <p><a href='/webhook-status'>Webhook Status</a></p>
    <p><a href='/debug-routes'>Debug Routes</a></p>
    <p>Bot is working correctly!</p>
    """

@flask_app.route('/test', methods=["GET"])
def test_endpoint():
    print("📍 /test endpoint accessed")
    return f'<h1>Test endpoint working!</h1><p>Webhook URL: https://telegram-bot-inkarshokan.replit.app/{TOKEN}</p><p>Current time: {__import__("datetime").datetime.now()}</p>'

@flask_app.route('/webhook-status')
def webhook_status():
    """Check webhook status via web endpoint"""
    print("📍 /webhook-status endpoint accessed")
    try:
        status = bot.get_webhook_info()  # No asyncio needed!
        return f"""
        <h1>Webhook Status</h1>
        <p><strong>URL:</strong> {status.url}</p>
        <p><strong>Pending Updates:</strong> {status.pending_update_count}</p>
        <p><strong>Max Connections:</strong> {status.max_connections}</p>
        <p><strong>IP Address:</strong> {status.ip_address}</p>
        <p><strong>Last Error:</strong> {status.last_error_message or 'None'}</p>
        <p><strong>Has Certificate:</strong> {status.has_custom_certificate}</p>
        """
    except Exception as e:
        print(f"❌ Error in /webhook-status: {e}")
        return f"<h1>Error checking webhook: {e}</h1>", 500

@flask_app.route('/debug-routes')
def debug_routes():
    """Debug route to show all registered routes"""
    print("📍 /debug-routes endpoint accessed")
    routes = []
    for rule in flask_app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    return "<h1>Registered Routes</h1><br>" + "<br>".join(routes)

@flask_app.route(f"/{TOKEN}", methods=["GET", "POST"])
def webhook():
    print(f"🔄 Received {request.method} request to webhook endpoint")

    if request.method == "GET":
        return 'Webhook endpoint is active', 200

    try:
        json_data = request.get_json(force=True)
        if not json_data:
            return 'Bad Request - No JSON', 400

        print(f"📥 Received webhook data: {json_data}")

        # Create update object and process it
        update = Update.de_json(json_data, bot)
        if update:
            print(f"📨 Processing update {update.update_id}")
            dispatcher.process_update(update)  # Synchronous processing!
            return 'OK', 200
        else:
            return 'Bad Request - Invalid Update', 400

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return 'Internal Server Error', 500

def setup_webhook():
    """Set the webhook URL for the bot"""
    webhook_url = f"https://telegram-bot-inkarshokan.replit.app/{TOKEN}"
    try:
        # Clear webhook first
        bot.delete_webhook(drop_pending_updates=True)
        print("🧹 Cleared old webhook and pending updates")

        # Set new webhook
        bot.set_webhook(webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")

        # Verify webhook
        webhook_info = bot.get_webhook_info()
        print(f"✅ Webhook verified: {webhook_info.url}")

    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")

print("🔁 New version launched with synchronous python-telegram-bot v13.15")