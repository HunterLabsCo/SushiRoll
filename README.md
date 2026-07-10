# Pokémon Restock Monitor 🔴

A little robot that watches **Target** and **Walmart** for Pokémon cards and
**texts Sandra on Telegram the second something comes in stock** — online *or*
at your Waterbury, CT stores. She taps the link and buys it herself.

It does **not** auto-buy. That's on purpose (see "Honest notes" at the bottom).

You do **not** need to know how to code to set this up. Follow the steps.

---

## What you'll end up with

- Runs **24/7 in the cloud for free** (GitHub Actions). Your laptop can be off.
- Checks every ~5 minutes.
- Sends a Telegram message like:
  > 🔴 **POKEMON RESTOCK**
  > Scarlet & Violet Elite Trainer Box
  > Available: ONLINE + IN STORE (Waterbury)
  > 👉 BUY NOW

---

## Setup — do this once (about 20–30 min)

### Step 1 — Make the Telegram bot (5 min)
1. Install **Telegram** on your phone (and Sandra's).
2. In Telegram, search for **@BotFather**, tap Start.
3. Send `/newbot`. Give it any name and username (must end in `bot`).
4. BotFather gives you a **token** — a long string like `8123456789:AAH...`.
   Copy it somewhere safe. This is your `TELEGRAM_TOKEN`.
5. Now search for the bot you just made and send it a message — type `hi`.
   - Want Sandra to get the alerts? Have **her** message the bot from her phone.
   - Want both of you? Make a Telegram **group**, add the bot to it, and send a
     message in the group.

### Step 2 — Get your Chat ID (2 min)
The bot needs to know *where* to send alerts. Easiest way:
- Open this link in a browser, replacing `<TOKEN>` with your token:
  `https://api.telegram.org/bot<TOKEN>/getUpdates`
- Look for `"chat":{"id":  ...}`. That number is your **`TELEGRAM_CHAT_ID`**.
  (Family group IDs start with a `-`. That's normal — include the minus sign.)

*(Or run `python get_chat_id.py` on a computer with Python — it prints it for you.)*

### Step 3 — Put the project on GitHub (10 min)
1. Make a free account at **github.com** if you don't have one.
2. Click **New repository** → name it `pokemon-restock` → set it to **Private**
   → **Create repository**.
3. Click **uploading an existing file** and drag in **all** the files from this
   folder (including the `.github` folder). Commit.

### Step 4 — Add your secrets (5 min)
In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret.**
Add these (name on the left, value on the right):

| Name | Value |
|------|-------|
| `TELEGRAM_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | the chat id from Step 2 |

(Leave `PROXY_URL` and `REDSKY_KEY` out for now — only needed later if Walmart
gets blocked or Target changes their key.)

### Step 5 — Add the products you want to watch
Open `config.json`. Your store info is already filled in for Waterbury:
- Target store `2156` (300 Chase Ave)
- Walmart store `3548` (910 Wolcott St)
- ZIP `06705`

Delete the two `EXAMPLE` lines and add the real products. For each one, just
paste the **product page URL**:

```json
{
  "zip": "06705",
  "target_store_id": "2156",
  "walmart_store_id": "3548",
  "check_online": true,
  "check_in_store": true,
  "realert_after_hours": 6,
  "products": [
    { "name": "Prismatic Evolutions ETB",        "url": "https://www.target.com/p/.../A-93954446" },
    { "name": "151 Booster Bundle (Walmart)",     "url": "https://www.walmart.com/ip/.../5689244557" }
  ]
}
```

**How to get a product URL:** search the item on target.com or walmart.com,
open the product page, and copy the address bar. That's it — the bot pulls the
ID out of the link automatically.

Commit the change on GitHub (pencil icon → edit → Commit).

### Step 6 — Turn it on
- Go to the **Actions** tab in your repo → if prompted, click to enable workflows.
- Click **Pokemon Restock Monitor** → **Run workflow** to test it right now.
- Click into the run and watch the log. You'll see each product and `IN STOCK`
  or `out`. If something's in stock, you'll get a Telegram ping. 🎉

From now on it runs itself every 5 minutes.

---

## Changing things later
- **Add/remove products:** edit `config.json` on GitHub.
- **Only want in-store, not online (or vice versa):** set `check_online` or
  `check_in_store` to `false`.
- **Getting pinged too often:** raise `realert_after_hours`.
- **Different stores:** change the store IDs (find them on the retailer's store
  locator page — the number is in the store URL).

---

## Honest notes (read these)

- **Target is reliable. Walmart is hit-or-miss.** Walmart fights bots hard, so
  its checks may show `BLOCKED` in the log. When that happens the fix is to route
  Walmart through a proxy — you have the **Bright Data** tool available for exactly
  this. See `CLAUDE_CODE_PROMPTS.md` (prompt #3) to wire it in. It costs a little
  money per check but makes Walmart dependable.
- **Dollar General & CVS aren't here on purpose.** They don't publish real-time
  online stock, so there's nothing for a bot to watch. For those, the move is
  *timing*: DG and CVS Pokémon usually hit shelves on weekly truck days — ask a
  store employee which day their trucks come and have Sandra swing by that morning.
- **This alerts; it doesn't buy.** Auto-checkout bots are what the scalpers run,
  they get accounts banned, and they violate store terms. An alert + a fast human
  tap is the safe, sustainable way to beat them to it.
- **Not into maintaining code?** Honest heads-up: paid services like Restockd,
  RestockR, TYPA, and Visualping already do this and email/Discord you. If this
  project ever feels like too much upkeep, those are a fine fallback.

Questions or something broke? Open this folder in **Claude Code** and paste one
of the prompts from `CLAUDE_CODE_PROMPTS.md`.
