from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters
import os

# =========================
# CONFIG
# =========================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE = -1002720231037  # your source
TARGET = -1002592856370  # your target

OLD_DELAY = 1.5
NEW_DELAY = 1.5

# =========================
# FLASK (KEEP ALIVE)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Forward Bot Running!"

# =========================
# FORWARD OLD HISTORY
# =========================
async def forward_old(bot):
    print("🔹 Starting old messages forwarding...")
    
    async for msg in bot.get_chat_history(SOURCE):
        try:
            await bot.copy_message(
                chat_id=TARGET,
                from_chat_id=SOURCE,
                message_id=msg.id
            )
            print(f"OLD → {msg.id}")
            await asyncio.sleep(OLD_DELAY)
        except Exception as e:
            print(f"Error OLD {msg.id}: {e}")
            await asyncio.sleep(OLD_DELAY * 2)

    print("✅ All old messages done!")


# =========================
# PYROGRAM START
# =========================
async def start_bot():
    bot = Client(
        "forwarder",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION
    )

    @bot.on_message(filters.chat(SOURCE))
    async def auto_forward(c, m):
        try:
            await bot.copy_message(
                chat_id=TARGET,
                from_chat_id=SOURCE,
                message_id=m.id
            )
            print(f"NEW → {m.id}")
            await asyncio.sleep(NEW_DELAY)
        except Exception as e:
            print(f"Error NEW {m.id}: {e}")
            await asyncio.sleep(NEW_DELAY * 2)

    await bot.start()
    print("🔥 Bot Started!")

    asyncio.create_task(forward_old(bot))

    await asyncio.Event().wait()


# =========================
# RUN THREAD
# =========================
def run_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

Thread(target=run_thread, daemon=True).start()

# =========================
# RUN FLASK
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
