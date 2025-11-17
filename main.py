from flask import Flask
from threading import Thread
import asyncio
from pyrogram import Client, filters

API_ID = 0               # <-- Your API_ID
API_HASH = ""            # <-- Your API_HASH
SESSION = ""             # <-- Your STRING SESSION
SOURCE = -1000000000000  # <-- Your source channel
DEST = -1000000000000    # <-- Your destination channel

app = Flask(__name__)

# ----------------------------------------
# PYROGRAM BOT (ASYNC + SAFE EVENT LOOP)
# ----------------------------------------
async def start_pyrogram():
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
    print("Bot Started Successfully!")
    await asyncio.Event().wait()  # keep alive forever

def run_pyrogram_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_pyrogram())

# Start Pyrogram in safe thread
Thread(target=run_pyrogram_in_thread, daemon=True).start()

# ----------------------------------------
# FLASK KEEP-ALIVE ROUTE
# ----------------------------------------
@app.route("/")
def home():
    return "Metflix Movie Forwarder is running!"

# ----------------------------------------
# RUN FLASK (Render uses port environment variable)
# ----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
