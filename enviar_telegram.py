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
        with open("pautas_traduzidas.json", "r", encoding="utf-8") as f:
            pautas = json.load(f)
    except FileNotFoundError:
        pautas = []

    if not pautas:
        enviar("🔎 <b>Monitor TJ-RJ</b>\n\nNenhum processo novo encontrado desde a última atualização.")
        print("Mensagem de 'sem novidades' enviada.")
        exit(0)

    header = "📋 <b>Monitor STJ — Novas pautas</b>\n\n"
    mensagens = []
    bloco_atual = header

    for i, p in enumerate(pautas, 1):
        angulos_txt = "\n".join(f"  • {a}" for a in p.get("angulos", []))
        bloco = (
            f"<b>{i}. {p.get('titulo', p.get('classe', 'Processo'))}</b>\n"
            f"📁 {p.get('numeroProcesso', '')}\n\n"
            f"{p.get('resumo_simples', '')}\n\n"
            f"💡 <i>{p.get('por_que_importa', '')}</i>\n\n"
            f"Ângulos de pauta:\n{angulos_txt}\n\n"
        )

        if len(bloco_atual) + len(bloco) > 4000:
            mensagens.append(bloco_atual)
            bloco_atual = bloco
        else:
            bloco_atual += bloco

    mensagens.append(bloco_atual)

    for msg in mensagens:
        if msg.strip():
            enviar(msg)
            print(f"Mensagem enviada ({len(msg)} caracteres)")

    print(f"Total: {len(pautas)} pautas enviadas ao Telegram.")

