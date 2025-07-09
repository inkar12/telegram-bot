# === main.py ===
import os
from bot import app

if __name__ == "__main__":
    print("🚀 Starting bot...")

    # Set your public Render URL here
    WEBHOOK_URL = f"https://your-render-app.onrender.com/{os.getenv('BOT_TOKEN')}"

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=WEBHOOK_URL
    )
