import os
import json
import requests
from datetime import datetime

TOKEN_BOT = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Tenta pegar a sua chave das Secrets. Se não existir, usa a chave pública padrão do DataJud CNJ
API_KEY = os.environ.get("DATAJUD_API_KEY") or "c3eae287-ba04-4990-8444-69777d72c36d" 

URL_DATAJUD = "https://api-publica.datajud.cnj.jus.br/api_v1_stj/_search"

def buscar_dados_datajud():
    headers = {
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": {
            "match_all": {}
        },
        "sort": [
            {"dataHoraModificacao": {"order": "desc"}}
        ],
        "size": 50
    }
    
    try:
        response = requests.post(URL_DATAJUD, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro na API DataJud: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def extrair_resumo(resultado):
    if not resultado or "hits" not in resultado or "hits" not in resultado["hits"]:
        return []
    
    lista_processos = []
    hits = resultado["hits"]["hits"]
    
    for hit in hits:
        fonte = hit.get("_source", {})
        num_processo = fonte.get("numeroProcesso", "Sem número")
        
        data_mod = fonte.get("dataHoraModificacao", "")
        data_formatada = "Data indisponível"
        if data_mod:
            try:
                dt = datetime.fromisoformat(data_mod.replace("Z", "+00:00"))
                data_formatada = dt.strftime("%d/%m/%Y %H:%M")
            except:
                data_formatada = data_mod
        
        movimentos = fonte.get("movimentos", [])
        ultima_mov = "Sem movimentação detalhada"
        if movimentos:
            ultimo_movimento = movimentos[-1]
            ultima_mov = ultimo_movimento.get("nome", "Movimentação desconhecida")
        
        lista_processos.append({
            "processo": num_processo,
            "data": data_formatada,
            "movimentacao": ultima_mov
        })
        
    return lista_processos

def enviar_telegram(processos):
    if not TOKEN_BOT or not CHAT_ID or not procesos:
        print("Configurações do Telegram ausentes ou lista de processos vazia.")
        return
    
    texto = "<b>📌 Monitor STJ - Processos Recentes</b>\n\n"
    for p in procesos[:5]:
        texto += f"🔹 <b>Proc:</b> {p['processo']}\n"
        texto += f"📅 <b>Modificado em:</b> {p['data']}\n"
        texto += f"📝 <b>Movimento:</b> {p['movimentacao']}\n\n"
        
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("Notificação enviada ao Telegram com sucesso!")
        else:
            print(f"Erro ao enviar Telegram: Status {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Erro na requisição do Telegram: {e}")

if __name__ == "__main__":
    print("Iniciando captura do DataJud...")
    dados = buscar_dados_datajud()
    
    if dados:
        processos = extrair_resumo(dados)
        
        if processos:
            print(f"Sucesso! {len(processos)} processos encontrados.")
            with open("pautas.json", "w", encoding="utf-8") as f:
                json.dump(processos, f, ensure_ascii=False, indent=4)
            
            enviar_telegram(processos)
        else:
            print("Nenhum processo formatado.")
    else:
        print("Falha ao obter dados da API.")
