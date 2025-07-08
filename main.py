import os
import bot

if __name__ == "__main__":
    print("🚀 Starting bot...")

    if os.getenv("RENDER") == "true":
        print("🛰️  Running on Render — setting webhook...")
        bot.setup_webhook()
    else:
        print("🧪 Running locally — skipping webhook setup")

    print("🔍 Registered routes:")
    for rule in bot.flask_app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")

    print("🌐 Starting Flask server...")
    bot.flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
