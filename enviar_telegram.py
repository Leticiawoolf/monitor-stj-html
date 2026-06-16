import os
import json
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def enviar(texto):
    resp = requests.post(URL, json={
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    })
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    try:
        with open("pautas.json", "r", encoding="utf-8") as f:
            pautas = json.load(f)
    except FileNotFoundError:
        print("pautas.json não encontrado.")
        exit(0)

    if not pautas:
        print("Nenhuma pauta para enviar.")
        exit(0)

    # Cabeçalho do boletim
    header = "📋 <b>Monitor STJ — Novas pautas</b>\n\n"
    mensagens = [header]
    bloco_atual = header

    for i, p in enumerate(pautas, 1):
        bloco = (
            f"<b>{i}. {p['titulo']}</b>\n"
            f"📁 {p.get('classe', '')} | 👤 {p.get('orgaoJulgador', '')}\n"
            f"📌 Assuntos: {', '.join(p.get('assuntos', []))}\n"
            f"🔄 Último movimento: {p.get('ultimoMovimento', '')} "
            f"({p.get('dataUltimoMovimento', '')})\n\n"
        )

        # Telegram tem limite de 4096 caracteres por mensagem
        if len(bloco_atual) + len(bloco) > 4000:
            mensagens.append(bloco_atual)
            bloco_atual = bloco
        else:
            bloco_atual += bloco

    mensagens.append(bloco_atual)

    # Remove o header duplicado se só teve uma mensagem
    if len(mensagens) == 2:
        mensagens = [mensagens[1]]

    for msg in mensagens:
        if msg.strip():
            enviar(msg)
            print(f"Mensagem enviada ({len(msg)} caracteres)")

    print(f"Total: {len(pautas)} pautas enviadas ao Telegram.")
