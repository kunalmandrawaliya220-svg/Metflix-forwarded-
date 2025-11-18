from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters
import os
import time

# =============================
# CONFIG (ALL IN ONE FILE)
# =============================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE = -1002720231037   # Source channel ID
DEST = -1002592856370     # Destination channel ID

OLD_MSG_DELAY = 3.0       # Delay for forwarding old messages (in seconds)
NEW_MSG_DELAY = 2.0       # Delay for forwarding new messages (in seconds)

# =============================
# FLASK APP
# =============================
app = Flask(__name__)

# =============================
# FORWARD OLD MESSAGES
# =============================
async def forward_old_messages(app2):
    print("🔹 Starting old messages forwarding...")
    async for msg in app2.get_chat_history(SOURCE):
        try:
            await msg.forward(DEST)
            print(f"Forwarded old message: {msg.id}")
            await asyncio.sleep(OLD_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding {msg.id}: {e}")
            await asyncio.sleep(OLD_MSG_DELAY * 2)
    print("✅ All old messages processed!")

# =============================
# START PYROGRAM CLIENT
# =============================
async def start_pyrogram():
    # 🔹 File-based session for stability (creates forwarder.session)
    app2 = Client(
        "forwarder",
        api_id=API_ID,
        api_hash=API_HASH
    )

    @app2.on_message(filters.chat(SOURCE))
    async def forward_handler(client, message):
        try:
            # Automatic forward: works for text, video, document, photo
            await message.forward(DEST)
            print(f"Forwarded NEW message: {message.id}")
            await asyncio.sleep(NEW_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding new message {message.id}: {e}")
            await asyncio.sleep(NEW_MSG_DELAY * 2)

    await app2.start()
    print("✅ Bot Started Successfully!")

    # Forward old messages in background
    asyncio.create_task(forward_old_messages(app2))

    # keep app running forever
    await asyncio.Event().wait()

# =============================
# RUN PYROGRAM IN THREAD
# =============================
def run_pyrogram_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_pyrogram())

Thread(target=run_pyrogram_in_thread, daemon=True).start()

# =============================
# FLASK ROUTE FOR KEEP-ALIVE
# =============================
@app.route("/")
def home():
    return "Forward Bot is running!"

# =============================
# RUN FLASK
# =============================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Render dynamic port
    app.run(host="0.0.0.0", port=PORT)
