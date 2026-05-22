import asyncio
import json
import random
import time
import os
from datetime import datetime
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
    flood_sleep_threshold=300
)

# ─────────────────────────────
# LOAD SAFE JSON
# ─────────────────────────────

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[WARN] {path}: {e}")
        return []

messages = load_json("messages.json")
groups = load_json("group.json")

immediate_groups = ["@ishugospozhy"]  # FIX: лучше username, не URL

delay = 3600

# ─────────────────────────────
# LOG
# ─────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ─────────────────────────────
# SEND CORE
# ─────────────────────────────

async def send_to_group(group, msg):
    try:
        await client.send_message(group, msg)
        log(f"[SEND] {group}: {msg[:40]}")

    except errors.FloodWaitError as e:
        log(f"[FLOOD] {group}: sleep {e.seconds}s")
        await asyncio.sleep(e.seconds + 1)

    except errors.SlowModeWaitError as e:
        log(f"[SLOWMODE] {group}: skip {e.seconds}s")

    except Exception as e:
        log(f"[ERROR] {group}: {e}")
        await asyncio.sleep(5)

# ─────────────────────────────
# LOOPS
# ─────────────────────────────

async def delayed_loop():
    while True:
        if not groups or not messages:
            log("No groups or messages loaded")
            await asyncio.sleep(30)
            continue

        for group in groups:
            msg = random.choice(messages)
            await send_to_group(group, msg)
            await asyncio.sleep(10)

        log("Cycle done (main groups)")
        await asyncio.sleep(delay)


async def immediate_loop():
    while True:
        if not immediate_groups or not messages:
            await asyncio.sleep(60)
            continue

        for group in immediate_groups:
            msg = random.choice(messages)
            await send_to_group(group, msg)
            await asyncio.sleep(10)

        log("Cycle done (immediate)")
        await asyncio.sleep(delay)


async def heartbeat():
    while True:
        log("BOT alive")
        await asyncio.sleep(300)

# ─────────────────────────────
# MAIN
# ─────────────────────────────

async def main():
    log("BOT starting")

    await client.start()

    log("BOT authorized")

    if not await client.is_user_authorized():
        raise RuntimeError("Not authorized session")

    log(f"Groups: {len(groups)} | Messages: {len(messages)}")

    await asyncio.gather(
        delayed_loop(),
        immediate_loop(),
        heartbeat()
    )

# ─────────────────────────────
# ENTRYPOINT (IMPORTANT FOR SYSTEMD)
# ─────────────────────────────

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log(f"FATAL: {e}")
