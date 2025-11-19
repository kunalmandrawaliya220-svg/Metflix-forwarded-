import os
import json
import asyncio
from threading import Thread
from time import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from flask import Flask
import traceback

API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION_STRING = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE = -1002720231037
DEST = -1002592856370

OLD_DELAY = 1.5
NEW_DELAY = 1.0
STATE_FILE = "state.json"

app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot forwarder running OK"

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_id": 0, "updated": 0}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

client = Client(
    "forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def forward_old():
    print("🔁 Starting old forward...")
    st = load_state()
    last_id = int(st.get("last_id", 0))

    async for m in client.get_chat_history(SOURCE, limit=0):
        try:
            if m.id <= last_id:
                continue

            await client.copy_message(DEST, SOURCE, m.id)
            print("OLD →", m.id)

            st["last_id"] = m.id
            st["updated"] = int(time())
            save_state(st)

            await asyncio.sleep(OLD_DELAY)

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print("Old error:", e)
            await asyncio.sleep(2)

    print("✔ Old forward done.")

@client.on_message(filters.chat(SOURCE))
async def _(c, m):
    try:
        await c.copy_message(DEST, SOURCE, m.id)
        print("NEW →", m.id)

        st = load_state()
        if m.id > st.get("last_id", 0):
            st["last_id"] = m.id
            st["updated"] = int(time())
            save_state(st)

        await asyncio.sleep(NEW_DELAY)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print("New error:", e)

async def start_bot():
    print("⚡ Starting Pyrogram client...")

    await client.start()
    print("🔥 User session started")

    try:
        chat = await client.get_chat(SOURCE)
        print("✓ SOURCE OK:", chat.title)
    except Exception as e:
        print("❌ SOURCE access fail:", e)
        traceback.print_exc()

    try:
        chat = await client.get_chat(DEST)
        print("✓ DEST OK:", chat.title)
    except:
        print("⚠ DEST warning (starting anyway)")

    asyncio.create_task(forward_old())

    await asyncio.Event().wait()

def run_thread():
    while True:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_bot())
        except Exception as e:
            print("🔥 BOT CRASHED — restarting in 5 sec")
            print(e)
            traceback.print_exc()
            import time
            time.sleep(5)

# FIX: daemon=False → Render will NOT kill bot thread
Thread(target=run_thread, daemon=False).start()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    print("Starting Flask on", PORT)
    app.run(host="0.0.0.0", port=PORT)
