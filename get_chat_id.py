#!/usr/bin/env python3
"""
One-time helper: finds your Telegram CHAT ID.

How to use:
  1. In Telegram, create a bot with @BotFather and copy the token it gives you.
  2. Start a chat with your new bot and send it any message (e.g. "hi").
     (If Sandra will get the alerts, have HER message the bot from her phone,
      or make a group, add the bot, and send a message in the group.)
  3. Run:  python get_chat_id.py   and paste the token when asked.
  4. It prints your CHAT ID. Save both the token and chat id -- you'll paste
     them into GitHub as secrets (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID).
"""

import requests

token = input("Paste your Telegram bot token: ").strip()
resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20).json()

if not resp.get("ok"):
    print("\nThat token didn't work. Double-check you copied the whole thing from BotFather.")
    raise SystemExit(1)

results = resp.get("result", [])
if not results:
    print(
        "\nNo messages found yet.\n"
        "Open Telegram, send your bot a message (any text), then run this again."
    )
    raise SystemExit(0)

seen = {}
for update in results:
    chat = (update.get("message") or update.get("channel_post") or {}).get("chat", {})
    if chat:
        seen[chat.get("id")] = chat.get("title") or chat.get("first_name") or "chat"

print("\nFound these chats (use the one that's you / your family group):\n")
for cid, name in seen.items():
    print(f"   CHAT ID: {cid}   ({name})")
