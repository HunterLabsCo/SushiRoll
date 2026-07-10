# Project Handoff & Session Roadmap

**Goal:** Alert Sandra (via Telegram) the instant Ascended Heroes Elite Trainer
Boxes become available at Target/Walmart — online, store pickup, or freshly
scanned into back stock at the Waterbury stores — so she can buy before scalpers.
The bot ALERTS only; a human always does the buying.

**Who does what:** Ricky runs the one-time setup. Sandra's whole experience is
Telegram: her phone buzzes → she taps BUY NOW.

---

## Where things stand
- ✅ Project built: `monitor.py`, `config.json`, GitHub Actions workflow, helper scripts.
- ✅ `config.json` is watching 4 Ascended Heroes ETB listings (3 Target, 1 Walmart)
  at Waterbury stores (Target 2156, Walmart 3548, ZIP 06705).
- ✅ Repo created by Ricky.
- ⏳ Next: run Session 1 to get it LIVE and tested.

## How we work
One Claude Code prompt (roughly one goal) per session. Do them in order. Each
prompt tells Claude Code to explain everything in plain English and to wait at
each step. Don't move to the next session until the current one is confirmed working.

---

## Session roadmap

**Session 1 — Get it live + tested + quantity tracking.** (Prompt below.)
Outcome: real Telegram test alert received; scheduled job running every 5 min;
back-stock quantity alerts added. This is THE important one.

**Session 2 — Make Walmart reliable with Bright Data.**
Only if Walmart checks show "BLOCKED". Use `CLAUDE_CODE_PROMPTS.md` Prompt #3.
Outcome: Walmart in-stock/quantity checks return real results. (Costs a little
per check — Claude Code will tell you how much.)

**Session 3 — Go faster than every 5 minutes.**
For hot online drops. `CLAUDE_CODE_PROMPTS.md` Prompt #5. Moves the bot to an
always-on host checking every 30–60 sec. Outcome: competitive on online drops.

**Session 4 — Phone status page (optional).**
`CLAUDE_CODE_PROMPTS.md` Prompt #7. A simple page you both can glance at.
Recommended host: Vercel (see plugins below).

**Session 5 — Add more stores / sets (as needed).**
`CLAUDE_CODE_PROMPTS.md` Prompt #6. E.g. Naugatuck Walmart 2284, or the next
Pokémon set when it's announced.

---

## Plugins / connectors worth turning on (honest picks)

Only three actually help this project. Ignore the rest.

1. **Bright Data** (already available) — the big one. It's how we make Walmart
   checks and back-stock quantity reliable through Walmart's bot blocking. Needed
   for Session 2. Costs a small amount per check; worth it for Walmart.

2. **Vercel** (available) — only if we do the status page (Session 4). Free tier
   is plenty. Lets Claude Code deploy the page for you in one step.

3. **GitHub connector** (available) — nice-to-have so that in future sessions I can
   look at your repo and check whether the scheduled Action is actually running
   and whether any runs failed, without you copy/pasting logs.

Not needed: the sales/marketing/legal/data connectors. They're for other kinds of
work and won't help here.

Note: some connectors may need you to authorize them first (in your Claude
connector settings). If one isn't connected when we need it, that's the fix.

---

## Facts to keep handy (so any future session has context)
- Retailers/stores: Target #2156 (300 Chase Ave), Walmart #3548 (910 Wolcott St),
  Waterbury CT, ZIP 06705.
- Product: Pokémon TCG *Mega Evolution — Ascended Heroes* ETBs (ME2.5), ~$59.99.
- Alerts: Telegram bot → family group (Ricky + Sandra).
- Secrets in GitHub: `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (later maybe `PROXY_URL`,
  `REDSKY_KEY`).
- Design choice: alert-only, never auto-buy (avoids bans/ToS issues; a fast human
  tap + in-store pickup is how a local family actually beats scalpers).
