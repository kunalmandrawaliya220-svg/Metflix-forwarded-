# main.py
import os
import json
import asyncio
from threading import Thread
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from flask import Flask

# ====================================
# CONFIG (Source = tumhara account, DEST channel)
# ====================================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION_STRING = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE_CHANNEL_ID = -1002537631509  # tumhara source channel
DEST_CHANNEL_ID   = -1003082074499  # destination channel

STATE_FILE = "state.json"
OLD_DELAY = 1.5
NEW_DELAY = 0.8

# ====================================
# Flask (keep-alive)
# ====================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot forwarder alive"

# ====================================
# State helpers
# ====================================
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_id": 0}

def save_state(st):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(st, f)
    except:
        pass

# ====================================
# Pyrogram Client (user session)
# ====================================
client = Client(
    "forwarder_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ====================================
# Forward old messages from SOURCE
# ====================================
async def forward_old():
    print("🔁 Scanning old messages...")
    st = load_state()
    last_id = int(st.get("last_id", 0))

    try:
        async for msg in client.get_chat_history(SOURCE_CHANNEL_ID, limit=0):
            if msg.id <= last_id:
                continue

            try:
                await client.copy_message(DEST_CHANNEL_ID, msg.chat.id, msg.id)
                print("OLD →", msg.id)

                st["last_id"] = msg.id
                save_state(st)

                await asyncio.sleep(OLD_DELAY)

            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print("Old error:", e)
                await asyncio.sleep(2)

    except Exception as e:
        print("❌ Cannot load old messages:", e)

    print("✔ Old forwarding completed (or nothing to sync).")

# ====================================
# Forward new messages in real-time
# ====================================
@client.on_message(filters.chat(SOURCE_CHANNEL_ID) & filters.me)
async def on_new(c, m):
    try:
        await c.copy_message(DEST_CHANNEL_ID, m.chat.id, m.id)
        print("NEW →", m.id)

        st = load_state()
        if m.id > st.get("last_id", 0):
            st["last_id"] = m.id
            save_state(st)

        await asyncio.sleep(NEW_DELAY)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print("New error:", e)

# ====================================
# Start bot
# ====================================
async def start_bot():
    await client.start()
    print("🔥 User session started")

    # validate SOURCE
    try:
        src = await client.get_chat(SOURCE_CHANNEL_ID)
        print("✓ SOURCE OK:", src.title)
    except Exception as e:
        print("❌ SOURCE not accessible:", e)
        raise SystemExit

    # validate DEST
    try:
        dest = await client.get_chat(DEST_CHANNEL_ID)
        print("✓ DEST OK:", dest.title)
    except Exception as e:
        print("⚠ DEST warning:", e)

    asyncio.create_task(forward_old())
    await asyncio.Event().wait()

# ====================================
# Thread runner
# ====================================
def run_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

Thread(target=run_thread, daemon=True).start()

# ====================================
# Flask main
# ====================================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    print("Starting Flask on", PORT)
    app.run(host="0.0.0.0", port=PORT)
