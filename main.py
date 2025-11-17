from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters
import os

app = Flask(__name__)

# ----------------------------------------
# ENV VARIABLES FOR RENDER (SAFE)
# ----------------------------------------
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION = os.getenv("SESSION", "")

SOURCE = int(os.getenv("SOURCE_CHANNEL", "-1000000000000"))
DEST = int(os.getenv("DEST_CHANNEL", "-1000000000000"))

# ----------------------------------------
# PYROGRAM BOT
# ----------------------------------------
async def start_pyrogram():
    if API_ID == 0 or API_HASH == "" or SESSION == "":
        print("❌ ERROR: API_ID / API_HASH / SESSION missing!")
        print("Set them in Render > Environment Variables")
        return

    app2 = Client(
        name="forwarder",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION,
        in_memory=True
    )

    @app2.on_message(filters.chat(SOURCE))
    async def forward_handler(client, message):
        try:
            await message.forward(DEST)
        except Exception as e:
            print("Forward Error:", e)

    await app2.start()
    print("✅ Forward Bot Started Successfully!")
    await asyncio.Event().wait()  # keep alive

def run_pyrogram_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_pyrogram())

# Start Pyrogram in background thread
Thread(target=run_pyrogram_in_thread, daemon=True).start()

# ----------------------------------------
# FLASK KEEP-ALIVE
# ----------------------------------------
@app.route("/")
def home():
    return "Metflix Movie Forwarder is running!"

# ----------------------------------------
# RUN FLASK
# ----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
