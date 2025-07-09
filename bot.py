# === bot.py (Refactored for python-telegram-bot v20.6) ===
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# === QUIZ LOGIC ===
questions = [
    {
        "text": "1\u20e3\ufe0f Какой у тебя средний GPA за последние 2 года?",
        "options": ["Ниже 2.5", "2.5–3.3", "3.4–3.8", "3.9–4.0"],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "2\u20e3\ufe0f Как ты оцениваешь свои внеклассные активности (спорт, волонтерство, проекты)?",
        "options": [
            "Пока нет достижений",
            "Есть базовые активности",
            "Хороший уровень участия",
            "Я лидер/создатель в чем-то",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "3\u20e3\ufe0f У тебя есть подтверждённый уровень английского языка?",
        "options": [
            "Нет, вообще",
            "Учусь, но без сертификатов",
            "Готовлюсь к IELTS/TOEFL",
            "Уже есть сертификат",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "4\u20e3\ufe0f Ты знаешь, куда именно хочешь поступать?",
        "options": [
            "Вообще нет",
            "Есть примерные идеи",
            "Выбрал страну и тип вуза",
            "Есть чёткий список вузов",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "5\u20e3\ufe0f Как ты оцениваешь свои шансы на стипендию?",
        "options": [
            "Не верю, что получу",
            "Сомневаюсь, но хочу",
            "Думаю, есть шанс",
            "Уверен(а) в себе",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "6\u20e3\ufe0f Как ты реагируешь, если что-то не получается — например, отказ в поступлении или плохая оценка?",
        "options": [
            "Осмысливаю и строю план камбэка",
            "Сомневаюсь, но продолжаю двигаться",
            "Махаю рукой — всегда есть другой путь",
            "Это сильно задевает, мне нужно время",
        ],
        "scores": [3, 2, 1, 0],
    },
    {
        "text": "7\u20e3\ufe0f Что больше всего мотивирует тебя поступать за границу?",
        "options": [
            "Свобода и независимость",
            "Сделать семью гордой",
            "Построить мощное будущее",
            "Найти себя и понять, кто я",
        ],
        "scores": [2, 1, 3, 2],
    },
    {
        "text": "8\u20e3\ufe0f Что для тебя будет самым важным после окончания учёбы?",
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = 0
    user_steps[user_id] = 0
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = user_steps[user_id]
    q = questions[step]
    markup = ReplyKeyboardMarkup(
        [[o] for o in q["options"]], one_time_keyboard=True, resize_keyboard=True
    )
    await context.bot.send_message(chat_id=user_id, text=q["text"], reply_markup=markup)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_steps:
        await context.bot.send_message(chat_id=user_id, text="Привет! Отправь /start чтобы начать квиз.")
        return

    step = user_steps[user_id]
    q = questions[step]

    if update.message.text not in q["options"]:
        await context.bot.send_message(chat_id=user_id, text="Пожалуйста, выбери один из предложенных вариантов.")
        return

    idx = q["options"].index(update.message.text)
    user_scores[user_id] += q["scores"][idx]
    user_steps[user_id] += 1

    if user_steps[user_id] < len(questions):
        await send_question(update, context)
    else:
        score = user_scores[user_id]
        if score <= 8:
            msg = "🟡 Ты — Исследователь.\nТы только в начале пути и тебе важно разобраться в возможностях, требованиях и стратегиях.\nНо это уже отличное начало!"
        elif score <= 16:
            msg = "🟢 Ты — Потенциальный кандидат.\nУ тебя уже есть подходящие идеи и навыки. Немного усилий — и ты сможешь собрать сильное портфолио и выиграть грант."
        else:
            msg = "🔵 Ты — Готовый аппликант.\nТы собрал всё нужное и готов к подаче. С правильной стратегией у тебя отличные шансы попасть в топ-вуз!"

        await context.bot.send_message(chat_id=user_id, text=f"Твой результат: {score}/24\n\n{msg}")
        await context.bot.send_message(chat_id=user_id, text=(
            "🎓 Я поступила в 16 вузов на полный грант и сейчас учусь в топовом liberal arts college в США.\n\n"
            "🔸 Первый раз — поступила туда, куда не хотела\n"
            "🔸 Второй — сильно старалась, но всё ещё не идеально\n"
            "🔸 Третий — правильная стратегия, правильный результат\n\n"
            "📌 У тебя тоже получится!"
        ))
        await context.bot.send_message(chat_id=user_id, text="💡 Хочешь бесплатную стратегию? Напиши результат менеджеру: @speakinkschool")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
async def main():
    print("🚀 Starting bot...")
    await app.initialize()
    await app.start_polling()
    await app.idle()
