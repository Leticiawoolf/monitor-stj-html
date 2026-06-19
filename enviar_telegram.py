import os
import json
import hashlib
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

ARQUIVO_HASH = "ultimo_envio_telegram.json"


def enviar(texto):
    resp = requests.post(URL, json={
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    })
    resp.raise_for_status()
    return resp.json()


def calcular_hash(pautas):
    """Gera um hash com base nos números de processo, para detectar se o
    conjunto de processos mudou desde o último envio ao Telegram."""
    numeros = sorted([p.get("numeroProcesso", "") for p in pautas])
    texto = "|".join(numeros)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def carregar_ultimo_hash():
    if os.path.exists(ARQUIVO_HASH):
        with open(ARQUIVO_HASH, "r") as f:
            return json.load(f).get("hash")
    return None


def salvar_ultimo_hash(hash_atual):
    with open(ARQUIVO_HASH, "w") as f:
        json.dump({"hash": hash_atual}, f)


if __name__ == "__main__":
    try:
        with open("pautas_traduzidas.json", "r", encoding="utf-8") as f:
            pautas = json.load(f)
    except FileNotFoundError:
        pautas = []

    if not pautas:
        enviar("🔎 <b>Monitor TJRJ</b>\n\nNenhum processo novo encontrado desde a última atualização.")
        print("Mensagem de 'sem novidades' enviada (pautas.json vazio).")
        exit(0)

    hash_atual = calcular_hash(pautas)
    hash_anterior = carregar_ultimo_hash()

    if hash_atual == hash_anterior:
        enviar("🔎 <b>Monitor TJRJ</b>\n\nNenhum processo novo encontrado desde a última atualização.")
        print("Mesmo conjunto de processos do último envio. Mensagem de 'sem novidades' enviada.")
        # Dashboard e Streamlit continuam mostrando os mesmos dados normalmente,
        # pois lêem pautas_traduzidas.json diretamente, sem depender deste hash.
        exit(0)

    # Conjunto de processos mudou: envia o conteúdo completo
    header = "📋 <b>Monitor TJRJ — Novas pautas</b>\n\n"
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

    salvar_ultimo_hash(hash_atual)
    print(f"Total: {len(pautas)} pautas enviadas ao Telegram. Hash atualizado.")
