import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.sessions import StringSession
from pyrogram.errors import FloodWait

# ====================================
# CREDENTIALS (YOUR REAL VALUES)
# ====================================
API_ID = 26361463
API_HASH = "3e6cb587c46f6829ff631a49a1d7261c"

SESSION_STRING = "BQGSPncAXM6WgyPpRQd3Miac9VvhJnb71jN0O_t_k8-4IQCDPDY4budIZQwjTDrFr4UnqM25k6vMX6QSo39ZfqZ66RjljDvnWTZ62IrD2Tn9ud4YP5yp-Jj1zp2uMQB8r0BsmBZd0wK8dub-moA8pBBGJf6lt1aHeZ_hE8L15L7WNDfjuYxBI_uk6MhKeSiW9-kwAAJUQlAy7BIl3d9_bWSL1BuAYVAwXQwuQBygObLk7Z8a8oimreb_o8XqD9HMAkTH7nyRT2Ld-QKiUshXWdfBXQHMSuc7xCw2OmWxdIybwHeBqug0TYAfLTwkq13iMp7jhWeH75u2sr4Kt-9TO8W-n-ZrPQAAAAF-rNmrAA"

# ====================================
# CHANNELS
# ====================================
SOURCE = -1002720231037          # Your source channel
TARGET = -1002592856370         # <-- Yaha target ID daalna (mujhe dedo)

# ====================================
# CREATE session file
# ====================================
with Client(StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH) as temp:
    print("🔥 forwarder.session created successfully!")

# ====================================
# MAIN CLIENT
# ====================================
app = Client(
    session_name="forwarder",          
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ====================================
# OLD MESSAGES FORWARD (UNLIMITED)
# ====================================
async def forward_old():
    print("⚡ Forwarding OLD messages...")
    async for msg in app.get_chat_history(SOURCE, limit=0):  # unlimited messages
        try:
            await msg.copy(TARGET)
        except FloodWait as e:
            print(f"⏳ FloodWait: {e.value}s wait")
            await asyncio.sleep(e.value)
        except Exception as err:
            print("❌ Error:", err)

        await asyncio.sleep(0.5)

    print("✅ OLD messages completed!")

# ====================================
# NEW MESSAGES AUTO-FORWARD
# ====================================
@app.on_message(filters.chat(SOURCE))
async def forward_new(c, msg):
    try:
        await msg.copy(TARGET)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as err:
        print("❌ Error:", err)

# ====================================
# START BOT
# ====================================
async def main():
    await app.start()
    print("🔥 BOT STARTED SUCCESSFULLY!")

    asyncio.create_task(forward_old())   # background old forward

    await idle()
    await app.stop()

asyncio.run(main())
