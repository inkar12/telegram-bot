import bot

if __name__ == "__main__":
    print("🚀 Starting bot...")
    bot.setup_webhook()
    print("🔍 Registered routes:")
    for rule in bot.flask_app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    print("🌐 Starting Flask server...")
    bot.flask_app.run(host="0.0.0.0", port=8080)
