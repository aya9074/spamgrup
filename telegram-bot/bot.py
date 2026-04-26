import asyncio
import json
import os
import time
from telethon import TelegramClient, errors

# ─────────────────────────────
# ENV CONFIG (SAFE)
# ─────────────────────────────

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env variable: {name}")
    return value

api_id = int(require_env("TELEGRAM_API_ID"))
api_hash = require_env("TELEGRAM_API_HASH")

session_name = "stable_session"

# ─────────────────────────────
# CLIENT
# ─────────────────────────────

client = TelegramClient(
    session_name,
    api_id,
    api_hash,
    auto_reconnect=True,
    connection_retries=-1,
    retry_delay=5,
    flood_sleep_threshold=300,
)

# ─────────────────────────────
# LOADERS (SAFE JSON)
# ─────────────────────────────

def load_json(path: str):
    if not os.path.exists(path):
        print(f"[WARN] Missing file: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return []

messages = load_json("messages.json")
groups = load_json("group.json")

immediate_groups = ["https://t.me/ishugospozhy"]

# ─────────────────────────────
# STATE STORAGE
# ─────────────────────────────

TS_MARKER_MAIN = "TS_MAIN:"
TS_MARKER_IMM = "TS_IMM:"

async def get_last_send(marker):
    try:
        async for msg in client.iter_messages("me", limit=50):
            if msg.text and msg.text.startswith(marker):
                return float(msg.text[len(marker):])
    except Exception as e:
        print(f"[WARN] timestamp read error: {e}")
    return None

async def save_last_send(marker):
    try:
        await client.send_message("me", f"{marker}{time.time()}")
    except Exception as e:
        print(f"[WARN] timestamp save error: {e}")

# ─────────────────────────────
# CORE LOOP (SAFE)
# ─────────────────────────────

async def main_loop():
    print("[BOT] started")

    await client.start()

    print("[BOT] authorized")

    while True:
        try:
            # здесь твоя логика отправки
            # пример heartbeat:
            print("[BOT] alive", time.strftime("%H:%M:%S"))

            await asyncio.sleep(60)

        except Exception as e:
            print(f"[ERROR] loop crashed: {e}")
            await asyncio.sleep(5)

# ─────────────────────────────
# ENTRYPOINT
# ─────────────────────────────

async def main():
    print("[BOT] starting...")

    await client.start()

    print("[BOT] authorized")

    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
