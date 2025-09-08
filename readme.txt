# KVFX Webhooks

FastAPI webhook that receives TradingView alerts and posts to Telegram.

**Endpoints**
- `POST /kvfx/webhook?token=WEBHOOK_TOKEN`
- `POST /tg/webhook?token=WEBHOOK_TOKEN`
- `GET  /healthz`

**Run**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
