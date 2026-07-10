# Copy/paste prompts for Claude Code

Open this folder in **Claude Code** (or Cowork), then paste any of these.
Each one is self-contained — just paste and hit enter.

---

### Prompt 1 — Test that everything works before I trust it
```
Run monitor.py locally in a test mode. Temporarily add one Pokemon product to
config.json that is DEFINITELY in stock right now on Target (pick a common item
and find its real TCIN), set my TELEGRAM_TOKEN and TELEGRAM_CHAT_ID as env vars
that I'll provide, and run the script so I get a real test alert on Telegram.
Then remove the test product. Walk me through it step by step — I don't code.
```

---

### Prompt 2 — Help me add the products Sandra wants
```
I want to watch these Pokemon products: [paste product names or paste the
target.com / walmart.com links]. Find the correct product URLs, add them to
config.json with clear names, remove the EXAMPLE entries, and double-check the
JSON is valid. Explain what you changed.
```

---

### Prompt 3 — Make Walmart reliable with Bright Data (do this if Walmart shows BLOCKED)
```
My Walmart checks are getting blocked. I have the Bright Data plugin available.
Set up Walmart checks to go through a Bright Data proxy/scraping so they stop
getting blocked. Add the credentials as a PROXY_URL GitHub secret (don't hardcode
them), update monitor.py if needed, and test that a Walmart product check now
returns a real in-stock / out-of-stock result. Explain the cost per check so I
know what I'm signing up for.
```

---

### Prompt 4 — Target checks stopped working (refresh the API key)
```
My Target checks in monitor.py started returning HTTP 401/403. The RedSky API
key probably rotated. Find the current public RedSky "key" value that target.com
uses, update the REDSKY_KEY default in monitor.py (or tell me to set it as a
GitHub secret), and verify a Target check works again.
```

---

### Prompt 5 — Run it faster than every 5 minutes
```
GitHub Actions only runs every 5 minutes and that's too slow for hot drops.
Move this monitor to an always-on host that can check every 30-60 seconds
(e.g. Railway or a small always-on process), keep the Telegram alerts and the
state.json de-duping working, and give me step-by-step deploy instructions for
a non-coder. Tell me the monthly cost.
```

---

### Prompt 6 — Add more stores or retailers
```
Add these to the monitor: [e.g. "the Naugatuck Walmart store 2284 too", or
"Best Buy and GameStop online"]. Update config.json and monitor.py as needed,
keep alerts and de-duping working, and test one check per new source.
```

---

### Prompt 7 — Add a simple status page (optional, deploy on Vercel)
```
Build a tiny web page that shows the current in-stock/out status of everything
in config.json, reading from state.json, and deploy it to Vercel so Sandra and I
can glance at it on our phones. Keep it dead simple. Give me the Vercel deploy
steps for a non-coder.
```
