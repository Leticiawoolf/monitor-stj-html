import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Monitor TJRJ — Busca por Assunto",
    page_icon="🔍",
    layout="centered"
)

DATAJUD_API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
ENDPOINT = "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"
HEADERS = {"Authorization": f"APIKey {DATAJUD_API_KEY}", "Content-Type": "application/json"}

TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")


def formatar_data(iso_str):
    if not iso_str or iso_str == "N/A":
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return iso_str


def buscar_por_assunto(termo, tamanho=50):
    query = {
        "size": tamanho,
        "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
        "query": {
            "match": {
                "assuntos.nome": {
                    "query": termo,
                    "operator": "and",
                    "fuzziness": "AUTO"
                }
            }
        }
    }
    resp = requests.post(ENDPOINT, json=query, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extrair_processos(resultado_json):
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
        })
    return processos


def enviar_telegram(texto):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    })
    return resp.status_code == 200


def formatar_para_telegram(processos, termo):
    if not processos:
        return f"🔍 <b>Busca: {termo}</b>\n\nNenhum processo encontrado."

    linhas = [f"🔍 <b>Busca: {termo}</b> — {len(processos)} resultado(s)\n"]
    for i, p in enumerate(processos[:10], 1):  # limita a 10 no Telegram
        assuntos = ", ".join(p["assuntos"][:2])
        linhas.append(
            f"<b>{i}. {p['classe'] or 'Processo'}</b>\n"
            f"📁 <code>{p['numeroProcesso']}</code>\n"
            f"📌 {assuntos}\n"
            f"👤 {p['orgaoJulgador'] or '—'}\n"
            f"🔄 {p['ultimoMovimento']} ({formatar_data(p['dataUltimoMovimento'])})\n"
        )
    if len(processos) > 10:
        linhas.append(f"<i>... e mais {len(processos) - 10} resultados. Veja todos no dashboard.</i>")
    return "\n".join(linhas)


# ── Interface ──────────────────────────────────────────────────────────────────
st.title("🔍 Busca de Processos — TJRJ")
st.caption("Busca direta na API DataJud/CNJ · Até 50 resultados por busca")

st.markdown("---")

# Campo de busca
termo = st.text_input(
    "Buscar por assunto",
    placeholder="Ex: superendividamento, acidente, progressão de regime...",
    help="Digite um termo relacionado ao assunto do processo. A busca aceita variações da palavra."
)

col1, col2 = st.columns([2, 1])
with col1:
    buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)
with col2:
    enviar = st.button("📨 Buscar e enviar ao Telegram", use_container_width=True)

if (buscar or enviar) and termo.strip():
    with st.spinner(f"Buscando processos sobre '{termo}'..."):
        try:
            resultado = buscar_por_assunto(termo.strip(), tamanho=50)
            processos = extrair_processos(resultado)
            total = resultado.get("hits", {}).get("total", {}).get("value", 0)

            st.success(f"**{len(processos)} processos encontrados** (total na base: {total})")

            if enviar and processos is not None:
                texto_telegram = formatar_para_telegram(processos, termo)
                ok = enviar_telegram(texto_telegram)
                if ok:
                    st.info("📨 Resultado enviado ao Telegram!")
                else:
                    st.warning("Não foi possível enviar ao Telegram. Verifique os secrets.")

            if not processos:
                st.info("Nenhum processo encontrado para esse termo. Tente outras palavras.")
            else:
                st.markdown("---")
                for p in processos:
                    assuntos = ", ".join(p["assuntos"]) or "—"
                    with st.expander(f"**{p['classe'] or 'Processo'}** · {assuntos}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Processo:** `{p['numeroProcesso']}`")
                            st.markdown(f"**Classe:** {p['classe'] or '—'}")
                            st.markdown(f"**Assuntos:** {assuntos}")
                        with c2:
                            st.markdown(f"**Órgão julgador:** {p['orgaoJulgador'] or '—'}")
                            st.markdown(f"**Último movimento:** {p['ultimoMovimento']} ({formatar_data(p['dataUltimoMovimento'])})")
                            st.markdown(f"**Indexado em:** {formatar_data(p['ultimaAtualizacao'])}")

        except requests.exceptions.ConnectTimeout:
            st.error("Timeout ao conectar com o DataJud. Tente novamente em instantes.")
        except Exception as e:
            st.error(f"Erro na busca: {type(e).__name__}: {e}")

elif (buscar or enviar) and not termo.strip():
    st.warning("Digite um termo de busca antes de pesquisar.")

st.markdown("---")
st.caption("Fonte: [DataJud/CNJ](https://datajud-wiki.cnj.jus.br) · [Voltar ao dashboard principal](./)")
