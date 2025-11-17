from pyrogram import Client, filters
from pyrogram.types import Message
import os
import asyncio
import json

# ----------------------------------------
# ENVIRONMENT VARIABLES (You will set them)
# ----------------------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE = int(os.environ.get("SOURCE_CHANNEL"))
DEST = int(os.environ.get("DEST_CHANNEL"))

# ----------------------------------------
# Save progress file
# ----------------------------------------
SAVE_FILE = "last_id.json"


def load_progress():
    if os.path.exists(SAVE_FILE):
        return json.load(open(SAVE_FILE))
    return {"last_id": 0}


def save_progress(msg_id):
    json.dump({"last_id": msg_id}, open(SAVE_FILE, "w"))


# ----------------------------------------
# Pyrogram client
# ----------------------------------------
app = Client(
    "forwarder",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# ----------------------------------------
# AUTO-FORWARD NEW MESSAGES
# ----------------------------------------
@app.on_message(filters.chat(SOURCE))
async def auto_forward_new(c, m: Message):
    try:
        await m.copy(DEST)
        print(f"New Forwarded: {m.id}")
    except Exception as e:
        print("New Forward Error:", e)


# ----------------------------------------
# FORWARD OLD MESSAGES
# ----------------------------------------
async def forward_old():
    await app.start()

    progress = load_progress()
    last = progress["last_id"]

    print(f"Resuming from old message ID: {last}")

    async for msg in app.get_chat_history(SOURCE, offset_id=last):
        try:
            if msg.media:
                await msg.copy(DEST)
                print(f"Old Forwarded: {msg.id}")
                save_progress(msg.id)
                await asyncio.sleep(0.3)  # floodwait safety
        except Exception as e:
            print("Old Forward Error:", e)

    print("All old messages forwarded!")
    await app.stop()


# ----------------------------------------
# RUN BOT
# ----------------------------------------
app.run(forward_old())
