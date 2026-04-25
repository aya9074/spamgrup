import asyncio
import json
import random
import time
from datetime import datetime
from telethon import TelegramClient, errors
api_id = 31752586
api_hash = "6464c3b248676c2610172f6ae3b92fca"
session_name = "stable_session"
TS_MARKER_MAIN = "TS_MAIN:"
TS_MARKER_IMM = "TS_IMM:"
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
messages = load_json("messages.json")
groups = load_json("group.json")
immediate_groups = ["https://t.me/ishugospozhy"]
delay = 3600
client = TelegramClient(session_name, api_id, api_hash,
    auto_reconnect=True, connection_retries=-1,
    retry_delay=5, flood_sleep_threshold=300)
async def get_last_send(marker):
    try:
        async for msg in client.iter_messages("me", limit=50):
            if msg.text and msg.text.startswith(marker):
                return float(msg.text[len(marker):])
    except Exception as e:
        print(f"Ошибка чтения timestamp: {e}")
    return None
async def save_last_send(marker):
    try:
        await client.send_message("me", f"{marker}{time.time()}")
    except Exception as e:
        print(f"Ошибка сохранения timestamp: {e}")
async def get_elapsed(marker):
    last = await get_last_send(marker)
    return float("inf") if last is None else time.time() - last
# ... остальные функции (send_to_group, delayed_loop, immediate_loop,
#     heartbeat_loop, connect_with_retry, main)
