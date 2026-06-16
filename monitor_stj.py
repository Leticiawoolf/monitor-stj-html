import os
import json
import requests
import time

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

def buscar_ultimas_atualizacoes(tamanho=50, ultimo_timestamp_processado=None):
    query = {
        "size": tamanho,
        "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
        "query": {"match_all": {}}
    }
    if ultimo_timestamp_processado:
        query["query"] = {
            "range": {"dataHoraUltimaAtualizacao": {"gt": ultimo_timestamp_processado}}
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

def extrair_resumo(resultado_json):
    processos = []
    for hit in resultado_json.get("hits", {}).get("hits", []):
        f = hit["_source"]
        movs = sorted(f.get("movimentos", []), key=lambda m: m.get("dataHora", ""))
        processos.append({
            "numeroProcesso": f.get("numeroProcesso"),
            "classe": f.get("classe", {}).get("nome"),
            "orgaoJulgador": f.get("orgaoJulgador", {}).get("nome"),
            "assuntos": [a.get("nome") for a in f.get("assuntos", [])],
            "ultimaAtualizacao": f.get("dataHoraUltimaAtualizacao"),
            "ultimoMovimento": movs[-1].get("nome") if movs else "N/A",
            "dataUltimoMovimento": movs[-1].get("dataHora") if movs else "N/A",
            "titulo": f"{f.get('classe', {}).get('nome', '')} — {', '.join([a.get('nome','') for a in f.get('assuntos', [])][:2])}",
        })
    return processos

if __name__ == "__main__":
    ultimo = carregar_ultimo_timestamp()
    resultado = buscar_ultimas_atualizacoes(tamanho=10, ultimo_timestamp_processado=ultimo)

    if resultado is None:
        exit(0)

    processos = extrair_resumo(resultado)

    if processos:
        novo_timestamp = processos[0]["ultimaAtualizacao"]
        if novo_timestamp != ultimo:
            print(f"Novo snapshot: {novo_timestamp} ({len(processos)} processos)")
            with open("pautas.json", "w", encoding="utf-8") as f:
                json.dump(processos, f, ensure_ascii=False, indent=2)
            salvar_ultimo_timestamp(novo_timestamp)
        else:
            print("Sem novidades.")
            with open("pautas.json", "w", encoding="utf-8") as f:
                json.dump([], f)
    else:
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
