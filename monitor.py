#!/usr/bin/env python3
"""
Pokemon card restock monitor.

What it does:
  - Reads config.json for a list of product URLs (Target + Walmart) to watch.
  - Checks each one for stock (online shipping AND your local Waterbury store pickup).
  - When something flips from out-of-stock to IN STOCK, it sends a Telegram alert.
  - Remembers what it already alerted (state.json) so it doesn't spam you,
    but will remind you again after `realert_after_hours` if it's still up.

This is an ALERT tool. It never buys anything. When Sandra gets the ping,
she taps the link and checks out herself.

Reliable for Target. Walmart is "best effort" because Walmart aggressively
blocks bots -- see README.md for the proxy upgrade if Walmart checks get blocked.
"""

import json
import os
import re
import sys
import time
from datetime import datetime

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
STATE_PATH = os.path.join(HERE, "state.json")

# Telegram credentials come from environment variables (set as GitHub secrets).
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Optional: route Walmart requests through a proxy (e.g. Bright Data) to beat
# bot detection. Leave unset to try direct (may get blocked).
PROXY_URL = os.environ.get("PROXY_URL", "").strip()

# Public web key RedSky uses for its aggregations API. If Target rotates it and
# Target checks start failing, grab a fresh one (see README) or set REDSKY_KEY.
REDSKY_KEY = os.environ.get("REDSKY_KEY", "9f36aeafbe60771e321a7cc95a78140772ab3e96").strip()

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def now_ts():
    return time.time()


# ---------------------------------------------------------------------------
# Figure out which retailer a URL is and pull its product id
# ---------------------------------------------------------------------------
def parse_product(url):
    url = url.strip()
    if "target.com" in url:
        m = re.search(r"/A-(\d+)", url)
        if m:
            return ("target", m.group(1))
    if "walmart.com" in url:
        m = re.search(r"/ip/(?:[^/]+/)?(\d+)", url)
        if m:
            return ("walmart", m.group(1))
    return (None, None)


# ---------------------------------------------------------------------------
# Target stock check via RedSky fulfillment API
# Returns dict: {"online": bool, "store": bool, "note": str}
# ---------------------------------------------------------------------------
def check_target(tcin, cfg):
    endpoint = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1"
    params = {
        "key": REDSKY_KEY,
        "tcin": tcin,
        "store_id": cfg["target_store_id"],
        "pricing_store_id": cfg["target_store_id"],
        "zip": cfg["zip"],
        "is_bot": "false",
    }
    try:
        r = requests.get(endpoint, params=params, headers=BROWSER_HEADERS, timeout=20)
        if r.status_code != 200:
            return {"online": False, "store": False, "note": f"HTTP {r.status_code}"}
        data = r.json()
    except Exception as e:  # noqa: BLE001
        return {"online": False, "store": False, "note": f"error: {e}"}

    fulfillment = (
        data.get("data", {})
        .get("product", {})
        .get("fulfillment", {})
    )

    online = False
    if cfg.get("check_online", True):
        ship = fulfillment.get("shipping_options", {}) or {}
        online = str(ship.get("availability_status", "")).upper() == "IN_STOCK"

    store = False
    if cfg.get("check_in_store", True):
        for opt in fulfillment.get("store_options", []) or []:
            pickup = (opt.get("order_pickup", {}) or {}).get("availability_status", "")
            drive = (opt.get("in_store_only", {}) or {}).get("availability_status", "")
            curb = (opt.get("curbside", {}) or {}).get("availability_status", "")
            if "IN_STOCK" in (str(pickup).upper(), str(drive).upper(), str(curb).upper()):
                store = True
                break

    return {"online": online, "store": store, "note": "ok"}


# ---------------------------------------------------------------------------
# Walmart stock check (best effort -- see README for the reliable proxy path)
# ---------------------------------------------------------------------------
def check_walmart(item_id, cfg):
    url = f"https://www.walmart.com/ip/{item_id}"
    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None
    try:
        r = requests.get(
            url,
            headers={**BROWSER_HEADERS, "Accept": "text/html,application/xhtml+xml"},
            proxies=proxies,
            timeout=25,
            verify=not bool(PROXY_URL),  # Bright Data residential often needs verify off
        )
    except Exception as e:  # noqa: BLE001
        return {"online": False, "store": False, "note": f"error: {e}"}

    if r.status_code in (403, 412) or "Robot or human" in r.text or "px-captcha" in r.text:
        return {"online": False, "store": False, "note": "BLOCKED (needs proxy)"}
    if r.status_code != 200:
        return {"online": False, "store": False, "note": f"HTTP {r.status_code}"}

    html = r.text
    # Walmart embeds a JSON blob; look for availabilityStatus.
    online = bool(re.search(r'"availabilityStatus"\s*:\s*"IN_STOCK"', html))
    # Rough add-to-cart signal as a backup.
    if not online and re.search(r'"canAddToCart"\s*:\s*true', html):
        online = True
    return {"online": online, "store": False, "note": "ok"}


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log("!! Telegram not configured (missing TELEGRAM_TOKEN / TELEGRAM_CHAT_ID). "
            "Would have sent:\n" + text)
        return False
    api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(
            api,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": "false",
            },
            timeout=20,
        )
        return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        log(f"Telegram send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    cfg = load_json(CONFIG_PATH, None)
    if not cfg:
        log("No config.json found. Aborting.")
        sys.exit(1)

    state = load_json(STATE_PATH, {})
    realert_secs = float(cfg.get("realert_after_hours", 6)) * 3600
    alerts_sent = 0

    for product in cfg.get("products", []):
        name = product.get("name", "Unknown")
        url = product.get("url", "")
        if name.startswith("EXAMPLE"):
            continue  # skip the sample rows

        retailer, pid = parse_product(url)
        if not retailer:
            log(f"Skipping (couldn't read URL): {name}")
            continue

        if retailer == "target":
            result = check_target(pid, cfg)
        else:
            result = check_walmart(pid, cfg)

        in_stock = result["online"] or result["store"]
        where = []
        if result["online"]:
            where.append("ONLINE")
        if result["store"]:
            where.append("IN STORE (Waterbury)")
        where_str = " + ".join(where) if where else "-"

        log(f"{retailer.upper():7} | {'IN STOCK' if in_stock else 'out':8} "
            f"| {where_str:25} | {result['note']:20} | {name}")

        key = f"{retailer}:{pid}"
        prev = state.get(key, {"in_stock": False, "last_alert": 0})
        last_alert = prev.get("last_alert", 0)

        # Alert when it flips to in-stock, OR it's still up past the cooldown.
        should_alert = in_stock and (
            not prev.get("in_stock", False)
            or (now_ts() - last_alert) > realert_secs
        )

        if should_alert:
            msg = (
                f"\U0001F534 <b>POKEMON RESTOCK</b>\n\n"
                f"<b>{name}</b>\n"
                f"Available: {where_str}\n\n"
                f"\U0001F449 <a href=\"{url}\">BUY NOW</a>\n\n"
                f"<i>(Go go go before it sells out)</i>"
            )
            if send_telegram(msg):
                log(f"   -> ALERT SENT: {name}")
                alerts_sent += 1
            state[key] = {"in_stock": True, "last_alert": now_ts()}
        else:
            state[key] = {"in_stock": in_stock, "last_alert": last_alert}

        time.sleep(2)  # be polite; don't hammer

    save_json(STATE_PATH, state)
    log(f"Done. {alerts_sent} alert(s) sent.")


if __name__ == "__main__":
    main()
