from pyrogram import Client, filters
from flask import Flask
import threading
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

SOURCE = int(os.getenv("SOURCE_CHANNEL"))
DEST = int(os.getenv("DEST_CHANNEL"))

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running Successfully!", 200


def start_bot():
    app2 = Client(
        name="forwarder",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        workers=4,
        in_memory=True
    )

    @app2.on_message(filters.chat(SOURCE))
    async def forward_messages(client, message):
        try:
            await message.copy(DEST)
            print("Forwarded:", message.id)
        except Exception as e:
            print("Error:", e)

    app2.run()


if __name__ == "__main__":
    # Run Bot in Background
    threading.Thread(target=start_bot).start()

    # Run Flask to satisfy Render (port required)
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
