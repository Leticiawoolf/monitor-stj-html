import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

resp = requests.post(URL, json={
    "chat_id": CHAT_ID,
    "text": "✅ <b>Teste Monitor STJ</b>\n\nBot funcionando corretamente!",
    "parse_mode": "HTML"
})

print(f"Status: {resp.status_code}")
print(f"Resposta: {resp.json()}")
