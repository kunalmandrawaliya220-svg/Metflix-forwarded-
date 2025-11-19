# main.py
import os
import json
import asyncio
from threading import Thread
from time import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from flask import Flask

# ============================
# CONFIG (already inserted)
# ============================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"
SESSION_STRING = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

SOURCE = -1002720231037   # source channel (you are member)
DEST   = -1002592856370   # destination channel (you are admin)

# tuning
OLD_DELAY = 1.5   # seconds between old messages (increase for heavy movies)
NEW_DELAY = 1.0   # seconds after copying a new message
STATE_FILE = "state.json"  # stores last forwarded message id to avoid duplicates
PEER_RESOLVE_RETRIES = 6
PEER_RESOLVE_WAIT = 2  # seconds between resolve retries

# =============================
# FLASK keep-alive (optional)
# =============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot forwarder running"

# =============================
# state helpers
# =============================
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_id": 0, "updated": 0}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print("State save error:", e)

# =============================
# Create pyrogram client (user session)
# =============================
client = Client(
    name="user_forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workdir="."
)

# =============================
# Utility: ensure we can access SOURCE (resolve peer)
# =============================
async def ensure_source_access():
    last_exc = None
    for attempt in range(1, PEER_RESOLVE_RETRIES + 1):
        try:
            # this will raise if peer invalid / not accessible
            chat = await client.get_chat(SOURCE)
            print(f"✅ Resolved source chat: {chat.title if hasattr(chat, 'title') else chat.id}")
            return True
        except RPCError as e:
            last_exc = e
            print(f"Warn: cannot resolve SOURCE (attempt {attempt}/{PEER_RESOLVE_RETRIES}): {e}")
            await asyncio.sleep(PEER_RESOLVE_WAIT)
        except Exception as e:
            last_exc = e
            print(f"Warn: unexpected resolve error (attempt {attempt}/{PEER_RESOLVE_RETRIES}): {e}")
            await asyncio.sleep(PEER_RESOLVE_WAIT)
    print("❌ Failed to resolve SOURCE after retries. Fix: ensure your user session is a member of SOURCE channel.")
    print("Last error:", last_exc)
    return False

# =============================
# Forward old history (skips already forwarded via state)
# =============================
async def forward_old():
    print("🔁 Starting old-history forward (may take time)...")
    state = load_state()
    last_id = int(state.get("last_id", 0))

    # iterate newest->oldest; skip ids <= last_id
    async for msg in client.get_chat_history(SOURCE, limit=0):
        try:
            if msg.id <= last_id:
                # skip already forwarded
                continue

            # copy message (no forwarded-from metadata)
            await client.copy_message(chat_id=DEST, from_chat_id=SOURCE, message_id=msg.id)
            print(f"OLD copied -> {msg.id}")
            # update state
            state["last_id"] = max(state.get("last_id", 0), msg.id)
            state["updated"] = int(time())
            save_state(state)

            await asyncio.sleep(OLD_DELAY)
        except FloodWait as e:
            wait = int(e.x) if hasattr(e, "x") else int(getattr(e, "value", 5))
            print(f"FloodWait {wait}s during old forward — sleeping")
            await asyncio.sleep(wait)
        except Exception as e:
            # log & continue
            print("Error copying old msg", getattr(msg, "id", None), "->", e)
            await asyncio.sleep(OLD_DELAY * 2)

    print("✅ Old-history forward finished (or no new old items).")

# =============================
# New messages handler
# =============================
@client.on_message(filters.chat(SOURCE))
async def on_new_message(_, message):
    try:
        await client.copy_message(chat_id=DEST, from_chat_id=SOURCE, message_id=message.id)
        print(f"NEW copied -> {message.id}")

        # update state to prevent duplicates later
        st = load_state()
        if message.id > st.get("last_id", 0):
            st["last_id"] = message.id
            st["updated"] = int(time())
            save_state(st)

        await asyncio.sleep(NEW_DELAY)
    except FloodWait as e:
        wait = int(e.x) if hasattr(e, "x") else int(getattr(e, "value", 5))
        print(f"FloodWait {wait}s on new message — sleeping")
        await asyncio.sleep(wait)
    except Exception as e:
        print("Error copying new msg", message.id, "->", e)

# =============================
# Bot (userbot) starter
# =============================
async def start_userbot():
    await client.start()
    print("🔥 User session started")

    ok = await ensure_source_access()
    if not ok:
        # stop client to avoid silent errors; exit so you can fix membership
        await client.stop()
        raise SystemExit("Source not accessible by this session. Make sure the session account is member of source channel.")

    # ensure DEST also accessible (we assume you are admin, but check)
    try:
        dest_chat = await client.get_chat(DEST)
        print("✅ Dest resolved:", getattr(dest_chat, "title", dest_chat.id))
    except Exception as e:
        print("Warn: cannot resolve DEST — ensure account has permission to post to DEST:", e)

    # start old-history forward in background
    asyncio.create_task(forward_old())

    # keep running
    await asyncio.Event().wait()

# =============================
# Run pyrogram in separate thread + Flask main thread
# =============================
def run_userbot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_userbot())
    except SystemExit as e:
        print("Exiting:", e)
    except Exception as e:
        print("Userbot crashed in thread:", e)

Thread(target=run_userbot_thread, daemon=True).start()

# =============================
# Launch Flask (main process)
# =============================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    print("Starting Flask on port", PORT)
    app.run(host="0.0.0.0", port=PORT)
