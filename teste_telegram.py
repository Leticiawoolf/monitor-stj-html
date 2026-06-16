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

testar-telegram:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install requests
      - name: Testar bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python teste_telegram.py
