# flask-discord-bot

A simple Flask application that stores messages in SQLite and forwards them to Discord via a webhook.

## Run

```bash
pip install -r requirements.txt
export DISCORD_WEBHOOK_URL="<your webhook url>"   # never commit this value
python app.py                                      # http://localhost:5001 (set PORT=8765 to change)
```

## Endpoints

- `GET /` – health message
- `POST /submit` with JSON `{"text": "hello"}` – saves to the DB and sends to Discord
- `GET /history` – messages from the last 30 minutes (UTC)

Set `FLASK_DEBUG=1` only for local development.
