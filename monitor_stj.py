import os
import json
import requests
import time

API_KEY = os.environ.get("DATAJUD_API_KEY", "")
ENDPOINT = "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"
HEADERS = {"Authorization": f"APIKey {API_KEY}", "Content-Type": "application/json"}


def buscar_ultimas_atualizacoes(tamanho=10):
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
    resultado = buscar_ultimas_atualizacoes(tamanho=10)

    if resultado is None or not resultado.get("hits", {}).get("hits"):
        print("API inacessível ou sem resultados.")
        with open("pautas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        exit(0)

    processos = extrair_resumo(resultado)
    print(f"{len(processos)} processos capturados (sempre os mais recentes do índice).")
    with open("pautas.json", "w", encoding="utf-8") as f:
        json.dump(processos, f, ensure_ascii=False, indent=2)
