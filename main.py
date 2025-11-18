from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters
import config  # <-- Config file import

# =====================================================
# CONFIG VARIABLES
# =====================================================
SOURCE = config.SOURCE
DEST = config.DEST

app = Flask(__name__)

# =====================================================
# OLD MESSAGES — SAFE CONTINUOUS FORWARDING
# =====================================================
async def forward_old_messages(app2):
    print("🔹 Starting old messages forwarding...")
    async for msg in app2.get_chat_history(SOURCE):
        try:
            await msg.forward(DEST)
            print(f"Forwarded old message: {msg.id}")
            await asyncio.sleep(config.OLD_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding {msg.id}: {e}")
            await asyncio.sleep(config.OLD_MSG_DELAY * 2)
    print("✅ All old messages processed!")

# =====================================================
# NEW MESSAGES AUTO-FORWARD
# =====================================================
async def start_pyrogram():
    app2 = Client(
        name="forwarder",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.SESSION,
        in_memory=True
    )

    @app2.on_message(filters.chat(SOURCE))
    async def forward_handler(client, message):
        try:
            await message.forward(DEST)
            print(f"Forwarded NEW message: {message.id}")
            await asyncio.sleep(config.NEW_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding new message {message.id}: {e}")
            await asyncio.sleep(config.NEW_MSG_DELAY * 2)

    await app2.start()
    print("✅ Bot Started Successfully!")

    # Forward old messages in background
    asyncio.create_task(forward_old_messages(app2))

    # keep app running forever
    await asyncio.Event().wait()

# =====================================================
# START BOT THREAD
# =====================================================
def run_pyrogram_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_pyrogram())

Thread(target=run_pyrogram_in_thread, daemon=True).start()

# =====================================================
# FLASK KEEP-ALIVE
# =====================================================
@app.route("/")
def home():
    return "Forward Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
