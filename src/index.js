export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Simple auth
    const token = url.searchParams.get("token");
    if (!env.WEBHOOK_TOKEN || token !== env.WEBHOOK_TOKEN) {
      return new Response("Bad token", { status: 401 });
    }

    // Health check
    if (url.pathname === "/healthz") {
      return new Response(JSON.stringify({ ok: true }), {
        headers: { "content-type": "application/json" },
      });
    }

    // TradingView → Telegram
    if (url.pathname === "/kvfx/webhook" && request.method === "POST") {
      const payload = await request.json();
      const s = payload.signal ?? {};
      const m = payload.market ?? {};
      const r = payload.risk ?? {};
      const x = s.extras ?? {};
      const text = [
        `🧭 <b>${payload.product || "KVFX"}</b> • <code>${m.symbol || "?"}</code> ${s.direction || "?"}`,
        `🔔 <b>${s.type || "?"}</b>  | 💪 ${s.strength ?? "—"}/5  | 🤖 conf ${(s.confidence ?? 0).toFixed(2)}`,
        `⏱ TF: ${x.tf || m.timeframe || "—"}  •  💵 ${m.price ?? "—"}`,
        `🎯 TP: ${r.tp ?? "—"}  •  🛡 SL: ${r.sl ?? "—"}  •  Risk%: ${r.riskPct ?? "—"}`,
        `🔗 Chart: ${(payload.meta ?? {}).chart_url || "—"}`
      ].join("\n");

      const form = new URLSearchParams({
        chat_id: env.CHAT_ID,
        text,
        parse_mode: "HTML",
        disable_web_page_preview: "true"
      });

      const tg = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
        method: "POST",
        body: form
      });

      if (!tg.ok) return new Response("Telegram error", { status: 500 });
      return new Response(JSON.stringify({ ok: true }), {
        headers: { "content-type": "application/json" },
      });
    }

    return new Response("Not found", { status: 404 });
  }
}
