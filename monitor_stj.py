import os
import json
import requests
import time
from datetime import datetime, timedelta, timezone

API_KEY = os.environ.get("DATAJUD_API_KEY", "")
ENDPOINT = "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search"
HEADERS = {"Authorization": f"APIKey {API_KEY}", "Content-Type": "application/json"}
ARQUIVO_ESTADO = "estado_stj.json"


def carregar_ultimo_timestamp():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r") as f:
            return json.load(f).get("ultimo_timestamp")
    return None


def salvar_ultimo_timestamp(timestamp):
    with open(ARQUIVO_ESTADO, "w") as f:
        json.dump({"ultimo_timestamp": timestamp}, f)


def buscar_ultimas_atualizacoes(tamanho=50):
    query = {
        "size": tamanho,
        "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
        "query": {"match_all": {}}
    }

    for i in range(3):
        try:
            resp = requests.post(ENDPOINT, json=query, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectTimeout:
            print(f"Timeout na tentativa {i+1}/3. Aguardando 10s...")
            if i < 2:
                time.sleep(10)
            else:
                print("API inacessível após 3 tentativas.")
                return None


def extrair_resumo(resultado_json, dias=60):
    processos = []
    limite = datetime.now(timezone.utc) - timedelta(days=dias)

    for hit in resultado_json.get("hits", {}).get("hits", []):
        f = hit["_source"]
        movs = sorted(f.get("movimentos", []), key=lambda m: m.get("dataHora", ""))

        if not movs:
            continue

        data_ultimo_mov = movs[-1].get("dataHora", "")
        try:
            dt = datetime.fromisoformat(data_ultimo_mov.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue

        if dt < limite:
            continue

        processos.append({
            "numeroProcesso": f.get("numeroProcesso"),
            "classe": f.get("classe", {}).get("nome"),
            "orgaoJulgador": f.get("orgaoJulgador", {}).get("nome"),
            "assuntos": [a.get("nome") for a in f.get("assuntos", [])],
            "ultimaAtualizacao": f.get("dataHoraUltimaAtualizacao"),
            "ultimoMovimento": movs[-1].get("nome"),
            "dataUltimoMovimento": data_ultimo_mov,
            "titulo": f"{f.get('classe', {}).get('nome', '')} — {', '.join([a.get('nome','') for a in f.get('assuntos', [])][:2])}",
        })

    processos.sort(key=lambda x: x["dataUltimoMovimento"], reverse=True)
    return processos[:10]


if __name__ == "__main__":
    ultimo = carregar_ultimo_timestamp()
    resultado = buscar_ultimas_atualizacoes(tamanho=50)

    if resultado is None:
        print("API inacessível. Mantendo pautas.json vazio para indicar indisponibilidade.")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        exit(0)

    if not resultado["hits"]["hits"]:
        print("Nenhum resultado retornado pela API.")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        exit(0)

    novo_timestamp = resultado["hits"]["hits"][0]["_source"].get("dataHoraUltimaAtualizacao")

    # Compara com o último timestamp salvo: se for igual, não há novidade real no índice
    if novo_timestamp == ultimo:
        print(f"Mesmo snapshot de antes ({novo_timestamp}). Sem novidades.")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        exit(0)

    # Timestamp novo: processa e salva
    processos = extrair_resumo(resultado, dias=60)

    if processos:
        print(f"Novo snapshot: {novo_timestamp} ({len(processos)} processos com movimentação recente)")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump(processos, f, ensure_ascii=False, indent=2)
    else:
        print(f"Novo snapshot ({novo_timestamp}), mas nenhum processo dentro da janela de dias definida.")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)

    salvar_ultimo_timestamp(novo_timestamp)
