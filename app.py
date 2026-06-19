import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="Monitor TJRJ — Sugestões de Pauta",
    page_icon="⚖️",
    layout="centered"
)

ARQUIVO_PAUTAS = "pautas_traduzidas.json"


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


# Header
st.title("⚖️ Monitor TJRJ")
st.caption("Pautas traduzidas com IA · Fonte: DataJud/CNJ via GitHub Actions · Atualização automática a cada 3h")

pautas = carregar_pautas()

# Estatísticas
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
            # Metadados básicos
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.markdown(f"**Órgão julgador:** {p.get('orgaoJulgador', '—')}")
                st.markdown(f"**Processo:** `{p.get('numeroProcesso', '—')}`")
            with meta_col2:
                st.markdown(f"**Último movimento:** {formatar_data(p.get('dataUltimoMovimento'))}")
                st.markdown(f"**Indexado em:** {formatar_data(p.get('ultimaAtualizacao'))}")

            st.divider()

            # Tradução
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
            st.caption(
                "A data de indexação indica quando esse registro foi atualizado na base "
                "do CNJ, podendo ser diferente da data do último movimento processual real."
            )

st.divider()
st.caption("Fonte: [DataJud/CNJ](https://datajud-wiki.cnj.jus.br) · tradução gerada por IA (Gemini)")
