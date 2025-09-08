from fastapi import FastAPI, Request, HTTPException
import os, json, time
import httpx

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DEFAULT_CHAT = os.getenv("TELEGRAM_CHANNEL_ID", "")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")

RECENT_KEYS = {}
LAST_SIGNAL_BY_CHAT = {}

def now_s(): return int(time.time())

def require_token(token: str):
    if not WEBHOOK_TOKEN or token != WEBHOOK_TOKEN:
        raise HTTPException(401, "Bad token")

def is_dupe(key: str, ttl=90) -> bool:
    t = now_s()
    if key in RECENT_KEYS and (t - RECENT_KEYS[key]) < ttl: return True
    RECENT_KEYS[key] = t
    if len(RECENT_KEYS) > 5000:
        cutoff = t - ttl
        for k, ts in list(RECENT_KEYS.items()):
            if ts < cutoff: del RECENT_KEYS[k]
    return False

async def tg_send(text: str, chat_id: str):
    if not BOT_TOKEN: raise HTTPException(500, "BOT token missing")
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        ); r.raise_for_status()

def fmt_signal(p: dict) -> str:
    s, m, r, x = p.get("signal", {}), p.get("market", {}), p.get("risk", {}), p.get("signal", {}).get("extras", {})
    lines = [
        f"🧭 <b>{p.get('product','KVFX')}</b> • <code>{m.get('symbol','?')}</code> {s.get('direction','?')}",
        f"🔔 <b>{s.get('type','?')}</b> | 💪 {s.get('strength','—')}/5 | 🤖 conf {float(s.get('confidence',0)):.2f}",
        f"⏱ TF: {x.get('tf', m.get('timeframe','—'))} • 💵 {m.get('price','—')}",
        f"🎯 TP: {r.get('tp','—')} • 🛡 SL: {r.get('sl','—')} • Risk%: {r.get('riskPct','—')}",
        f"🔗 Chart: {p.get('meta', {}).get('chart_url','—')}"
    ]; return "\n".join(lines)

@app.get("/healthz")
def health(): return {"ok": True}

@app.post("/kvfx/webhook")
async def kvfx_webhook(request: Request):
    require_token(request.query_params.get("token",""))
    payload = json.loads((await request.body()).decode("utf-8"))
    key = f"{payload.get('market',{}).get('symbol','?')}|{payload.get('signal',{}).get('type','?')}|{payload.get('meta',{}).get('ts',now_s())}"
    if is_dupe(key): return {"ok": True, "deduped": True}
    chat_id = DEFAULT_CHAT or payload.get("chat_id", DEFAULT_CHAT)
    LAST_SIGNAL_BY_CHAT[str(chat_id)] = payload
    await tg_send(fmt_signal(payload), chat_id)
    return {"ok": True}

@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    require_token(request.query_params.get("token",""))
    u = await request.json(); msg = u.get("message") or u.get("channel_post")
    if not msg: return {"ok": True}
    chat_id = msg["chat"]["id"]; text = (msg.get("text") or "").strip()

    if text.startswith("/risk"):
        parts = text.split()
        if len(parts) < 5:
            return await tg_send("Usage: /risk <balance> <riskPct> <entry> <sl>", chat_id)
        bal, rpct, entry, sl = map(float, parts[1:5])
        risk_amt = bal*(rpct/100); delta = abs(entry-sl)
        if delta == 0: return await tg_send("Error: SL equals Entry.", chat_id)
        units = risk_amt/delta
        return await tg_send(
            f"🧮 Risk Coach\nBalance: {bal:.2f}\nRisk%: {rpct:.2f}% → ${risk_amt:.2f}\n"
            f"Entry: {entry} | SL: {sl} | Δ: {delta:.5f}\nSuggested Units: <b>{units:.2f}</b>", chat_id)

    if text.startswith("/explain"):
        p = LAST_SIGNAL_BY_CHAT.get(str(chat_id))
        if not p: return await tg_send("No recent signal cached for this chat yet.", chat_id)
        s, m, r, x = p["signal"], p["market"], p.get("risk",{}), p["signal"].get("extras",{})
        return await tg_send(
            "🧠 <b>Why this fired</b>\n"
            f"- Type: {s.get('type')} • Dir: {s.get('direction')}\n"
            f"- TF: {x.get('tf', m.get('timeframe','?'))} • Price: {m.get('price')}\n"
            f"- Filters: {', '.join(x.get('filters', [])) or '—'}\n"
            f"- Strength: {s.get('strength','—')}/5 • Conf: {s.get('confidence','—')}\n"
            f"- SL: {r.get('sl','—')} • TP: {r.get('tp','—')}\n"
            "Matches your KVFX playbook. Use /risk to size.", chat_id)

    if text.startswith("/help"):
        return await tg_send("Commands:\n/risk <balance> <riskPct> <entry> <sl>\n/explain\n/help", chat_id)
    return {"ok": True}
