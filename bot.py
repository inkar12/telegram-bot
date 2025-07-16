# === bot.py ===
import os
import json
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# === Вопросы ===
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
        "text": "4\u20e3\ufe0f В какие страны ты планируешь подавать?\n(Выбери все, что подходят. Когда закончишь — нажми «Готово»)",
        "options": [
            "🇺🇸 США", "🇬🇧 Великобритания", "🇨🇦 Канада",
            "🇪🇺 Европа (\u0413\u0435\u0440\u043c\u0430\u043d\u0438\u044f, \u0424\u0440\u0430\u043d\u0446\u0438\u044f \u0438 \u0434\u0440.)",
            "🇦🇺 Авст\u0440\u0430\u043b\u0438\u044f/Н\u043e\u0432\u0430\u044f \u0417\u0435\u043b\u0430\u043d\u0434\u0438\u044f", "🇰🇷🇯🇵 Азия (Корея, Япония и др.)",
            "🌍 Другое", "✅ Готово"
        ],
        "scores": [1, 1, 1, 1, 1, 1, 1, 0],
        "multi_select": True
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
        "text": "8\u20e3\ufe0f Начал(а) ли ты писать Personal Statement или Statement of Purpose на английском?",
        "options": [
            "Нет, пока не понимаю, как вообще подступиться",
            "Есть черновик, но он сырой и не про меня",
            "Начал(а), стараюсь раскрыть свои смыслы, но не уверен(а)",
            "Да, написал(а) эссе с глубокой идеей и сильной подачей",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "9\u20e3\ufe0f Сколько ты готов(а) вложить в свою подготовку к поступлению (курсы, консультанты, тесты и т.п.)?",
        "options": [
            "Ничего, рассчитываю только на бесплатное",
            "До $300 (базовый уровень)",
            "От $300 до $1000 — готов(а) инвестировать в качественную подготовку",
            "Больше $1000 — понимаю важность вложений в результат",
        ],
        "scores": [0, 1, 2, 3],
    },
    {
        "text": "🔟 Сколько ты планируешь тратить на обучение и жизнь за границей в год (если не получишь полную стипендию)?",
        "options": [
            "Ничего — только стипендия, иначе не поеду",
            "До $5,000 в год могу найти/накопить",
            "До $15,000 — с частичной поддержкой от семьи",
            "$20,000+ — семья готова инвестировать, если поступлю в хороший вуз",
        ],
        "scores": [0, 1, 2, 3],
    },
]

# === Состояния ===
user_scores = {}
user_steps = {}
user_answers = {}
user_multi_answers = {}

# === Команда /start ===
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_scores[user_id] = 0
    user_steps[user_id] = 0
    user_answers[user_id] = {
        "username": update.effective_user.username,
        "answers": [],
        "total_score": 0
    }
    send_question(update, context)

# === Отправка вопроса ===
def send_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    step = user_steps[user_id]
    q = questions[step]

    if q.get("multi_select") and user_id in user_multi_answers:
        current = user_multi_answers[user_id]["selected"]
        context.bot.send_message(chat_id=user_id, text=f"Вы уже выбрали: {', '.join(current)}")

    markup = ReplyKeyboardMarkup(
        [[o] for o in q["options"]],
        one_time_keyboard=not q.get("multi_select", False),
        resize_keyboard=True
    )
    context.bot.send_message(chat_id=user_id, text=q["text"], reply_markup=markup)

# === Ответ пользователя ===
def answer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in user_steps:
        context.bot.send_message(chat_id=user_id, text="Привет! Отправь /start чтобы начать квиз.")
        return

    step = user_steps[user_id]
    q = questions[step]
    text = update.message.text

    if q.get("multi_select"):
        if user_id not in user_multi_answers:
            user_multi_answers[user_id] = {"selected": [], "score": 0}

        if text == "✅ Готово":
            user_scores[user_id] += user_multi_answers[user_id]["score"]
            user_answers[user_id]["answers"].append({
                "question": q["text"],
                "answer": user_multi_answers[user_id]["selected"],
                "score": user_multi_answers[user_id]["score"]
            })
            user_steps[user_id] += 1
            del user_multi_answers[user_id]
        elif text in q["options"] and text not in user_multi_answers[user_id]["selected"]:
            user_multi_answers[user_id]["selected"].append(text)
            idx = q["options"].index(text)
            user_multi_answers[user_id]["score"] += q["scores"][idx]
        else:
            context.bot.send_message(chat_id=user_id, text="Выбери один из предложенных вариантов или нажми ✅ Готово")
            return
    else:
        if text not in q["options"]:
            context.bot.send_message(chat_id=user_id, text="Пожалуйста, выбери один из предложенных вариантов.")
            return

        idx = q["options"].index(text)
        user_scores[user_id] += q["scores"][idx]

        user_answers[user_id]["answers"].append({
            "question": q["text"],
            "answer": text,
            "score": q["scores"][idx]
        })
        user_steps[user_id] += 1

    if user_steps[user_id] < len(questions):
        send_question(update, context)
    else:
        score = user_scores[user_id]
        user_answers[user_id]["total_score"] = score

        os.makedirs("responses", exist_ok=True)
        with open(f"responses/user_{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(user_answers[user_id], f, ensure_ascii=False, indent=2)

        if score <= 10:
            msg = "🟡 Ты — Исследователь..."
        elif score <= 20:
            msg = "🟢 Ты — Потенциальный кандидат..."
        else:
            msg = "🔵 Ты — Готовый аппликант..."

        context.bot.send_message(chat_id=user_id, text=f"Твой результат: {score}/30\n\n{msg}")
        context.bot.send_message(chat_id=user_id, text=(
            "• Я поступила в 16 вузов США и в топ 30 liberal arts college на полный грант..."
        ))
        context.bot.send_message(chat_id=user_id, text=(
            "• Хочешь бесплатную стратегию для поступления в твой вуз мечты?\n"
            "Отправь скрин этого результата менеджеру: @speakinkschool"
        ))

# === Запуск бота ===
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    print("🚀 Бот запущен")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
