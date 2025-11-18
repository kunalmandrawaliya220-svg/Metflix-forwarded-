from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters

# ==============================
# CONFIG (Set your constants here)
# ==============================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION_STRING = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE = -1003228440842
DEST = -1002592856370

OLD_MSG_DELAY = 1.5  # seconds
NEW_MSG_DELAY = 1.5  # seconds

# ==============================
# FLASK KEEP-ALIVE
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Forward Bot is running!"

# ==============================
# OLD MESSAGES FORWARDING
# ==============================
async def forward_old_messages(bot):
    print("🔹 Starting old messages forwarding...")
    async for msg in bot.get_chat_history(SOURCE):
        try:
            await msg.forward(DEST)
            print(f"Forwarded OLD: {msg.id}")
            await asyncio.sleep(OLD_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding OLD {msg.id}: {e}")
            await asyncio.sleep(OLD_MSG_DELAY * 2)
    print("✅ All old messages processed!")

# ==============================
# NEW MESSAGES AUTO-FORWARD
# ==============================
async def start_pyrogram():
    bot = Client(
        name="forwarder",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

    @bot.on_message(filters.chat(SOURCE))
    async def forward_new(c, m):
        try:
            await m.forward(DEST)
            print(f"Forwarded NEW: {m.id}")
            await asyncio.sleep(NEW_MSG_DELAY)
        except Exception as e:
            print(f"Error forwarding NEW {m.id}: {e}")
            await asyncio.sleep(NEW_MSG_DELAY * 2)

    await bot.start()
    print("✅ Pyrogram Bot Started Successfully!")

    # Forward old messages in background
    asyncio.create_task(forward_old_messages(bot))

    # Keep running
    await asyncio.Event().wait()

# ==============================
# RUN PYROGRAM IN THREAD
# ==============================
def run_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_pyrogram())

Thread(target=run_bot_thread, daemon=True).start()

# ==============================
# RUN FLASK
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
