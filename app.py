import streamlit as st
import json
import os
import requests
from datetime import datetime

st.set_page_config(
    page_title="Monitor TJRJ — Sugestões de Pauta",
    page_icon="⚖️",
    layout="centered"
)

ARQUIVO_PAUTAS = "pautas_traduzidas.json"
DATAJUD_API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
ENDPOINT = "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search"


def carregar_pautas():
    if not os.path.exists(ARQUIVO_PAUTAS):
        return []
    with open(ARQUIVO_PAUTAS, "r", encoding="utf-8") as f:
        return json.load(f)


def formatar_data(iso_str):
    if not iso_str or iso_str == "N/A":
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        return iso_str


# ── Teste de conexão com DataJud ──────────────────────────────────────────────
with st.expander("🔧 Teste de conexão com DataJud (diagnóstico)", expanded=False):
    st.caption("Use este painel para verificar se o Streamlit Cloud consegue acessar a API do DataJud/CNJ.")
    if st.button("Testar conexão agora"):
        with st.spinner("Conectando..."):
            try:
                resp = requests.post(
                    ENDPOINT,
                    json={"size": 1, "query": {"match_all": {}}, "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}]},
                    headers={"Authorization": f"APIKey {DATAJUD_API_KEY}", "Content-Type": "application/json"},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    ultimo = data["hits"]["hits"][0]["_source"]["dataHoraUltimaAtualizacao"]
                    st.success(f"✅ Conexão OK! Último registro indexado em: {ultimo}")
                else:
                    st.error(f"❌ Erro HTTP {resp.status_code}: {resp.text[:200]}")
            except requests.exceptions.ConnectTimeout:
                st.error("❌ Timeout — Streamlit Cloud não consegue acessar o DataJud (mesmo bloqueio do GitHub Actions)")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {type(e).__name__}: {e}")

# ── Dashboard principal ───────────────────────────────────────────────────────
st.title("⚖️ Monitor TJRJ")
st.caption("Pautas traduzidas com IA · Fonte: DataJud/CNJ via GitHub Actions · Atualização automática a cada 3h")

pautas = carregar_pautas()

col1, col2, col3 = st.columns(3)
col1.metric("Processos encontrados", len(pautas))
col2.metric("Tribunal monitorado", "TJRJ")
if pautas:
    datas = [p.get("dataUltimoMovimento") for p in pautas if p.get("dataUltimoMovimento")]
    ultima = formatar_data(sorted(datas, reverse=True)[0]) if datas else "—"
else:
    ultima = "—"
col3.metric("Último movimento", ultima)

st.divider()

if not pautas:
    st.info("Nenhum processo com movimentação recente no momento.")
else:
    for i, p in enumerate(pautas):
        titulo = p.get("titulo") or f"{p.get('classe', 'Processo')} · {', '.join(p.get('assuntos', []))}"

        with st.expander(f"**{titulo}**"):
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.markdown(f"**Órgão julgador:** {p.get('orgaoJulgador', '—')}")
                st.markdown(f"**Processo:** `{p.get('numeroProcesso', '—')}`")
            with meta_col2:
                st.markdown(f"**Último movimento:** {formatar_data(p.get('dataUltimoMovimento'))}")
                st.markdown(f"**Indexado em:** {formatar_data(p.get('ultimaAtualizacao'))}")

            st.divider()

            tem_traducao = p.get("resumo_simples") or p.get("por_que_importa")

            if tem_traducao:
                st.markdown("##### 📝 Em linguagem simples")
                st.write(p.get("resumo_simples", "—"))

                st.markdown("##### 💡 Por que importa para você")
                st.write(p.get("por_que_importa", "—"))

                angulos = p.get("angulos", [])
                if angulos:
                    st.markdown("##### 🎯 Ângulos de pauta")
                    for a in angulos:
                        st.markdown(f"- {a}")

                glossario = p.get("glossario", [])
                if glossario:
                    st.markdown("##### 📖 Glossário do juridiquês")
                    for g in glossario:
                        st.markdown(f"**{g.get('termo', '')}**: {g.get('definicao', '')}")
            else:
                st.caption("Tradução ainda não disponível para este processo.")

            st.divider()
            st.markdown("##### Dados do processo")
            st.markdown(f"""
            - **Classe:** {p.get('classe', '—')}
            - **Assuntos:** {', '.join(p.get('assuntos', [])) or '—'}
            - **Último movimento:** {p.get('ultimoMovimento', '—')}
            """)

st.divider()
st.caption("Fonte: [DataJud/CNJ](https://datajud-wiki.cnj.jus.br) · tradução gerada por IA (Gemini)")
