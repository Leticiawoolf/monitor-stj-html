import streamlit as st
import requests
import json
from datetime import datetime
from google import genai
from google.genai import errors

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
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")


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


def traduzir_processo(processo):
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY não configurada nos secrets do Streamlit."
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""Você é o "JurisTradutor STF", um tradutor especialista em juridiquês brasileiro.
Traduza este processo judicial do TJRJ para linguagem simples e acessível ao público geral.

Processo:
{json.dumps(processo, ensure_ascii=False, indent=2)}

Retorne APENAS um objeto JSON com:
- "titulo": título de pauta em linguagem simples
- "resumo_simples": 2-3 frases explicando o que está em jogo, sem juridiquês
- "por_que_importa": 1-2 frases sobre o impacto para o cidadão comum
- "angulos": lista de 2-3 sugestões de ângulo de reportagem
- "glossario": lista de objetos {{"termo": ..., "definicao": ...}}

Sem markdown, sem texto adicional, só o JSON."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        texto = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(texto), None
    except errors.ServerError as e:
        return None, f"Gemini indisponível: {e}"
    except Exception as e:
        return None, f"Erro na tradução: {type(e).__name__}: {e}"


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
    for i, p in enumerate(processos[:10], 1):
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
st.caption("Busca direta na API DataJud/CNJ · Até 50 resultados · Tradução sob demanda via Gemini")

st.markdown("---")

termo = st.text_input(
    "Buscar por assunto",
    placeholder="Ex: superendividamento, acidente, progressão de regime...",
    help="A busca aceita variações da palavra automaticamente."
)

col1, col2 = st.columns([2, 1])
with col1:
    buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)
with col2:
    enviar = st.button("📨 Buscar e enviar ao Telegram", use_container_width=True)

# Inicializa estado de traduções na sessão
if "traducoes" not in st.session_state:
    st.session_state.traducoes = {}

if (buscar or enviar) and termo.strip():
    with st.spinner(f"Buscando processos sobre '{termo}'..."):
        try:
            resultado = buscar_por_assunto(termo.strip(), tamanho=50)
            processos = extrair_processos(resultado)
            total = resultado.get("hits", {}).get("total", {}).get("value", 0)
            st.session_state.processos = processos
            st.session_state.total = total
            st.session_state.termo = termo.strip()
            # Limpa traduções anteriores ao fazer nova busca
            st.session_state.traducoes = {}

            if enviar:
                texto_telegram = formatar_para_telegram(processos, termo)
                ok = enviar_telegram(texto_telegram)
                if ok:
                    st.info("📨 Resultado enviado ao Telegram!")
                else:
                    st.warning("Não foi possível enviar ao Telegram. Verifique os secrets.")

        except requests.exceptions.ConnectTimeout:
            st.error("Timeout ao conectar com o DataJud. Tente novamente em instantes.")
            st.stop()
        except Exception as e:
            st.error(f"Erro na busca: {type(e).__name__}: {e}")
            st.stop()

elif (buscar or enviar) and not termo.strip():
    st.warning("Digite um termo de busca antes de pesquisar.")

# Exibe resultados (mantidos na sessão entre interações)
if "processos" in st.session_state and st.session_state.processos is not None:
    processos = st.session_state.processos
    total = st.session_state.total
    termo_atual = st.session_state.termo

    st.success(f"**{len(processos)} processos encontrados** para '{termo_atual}' (total na base: {total})")
    st.markdown("---")

    for i, p in enumerate(processos):
        num = p["numeroProcesso"]
        assuntos = ", ".join(p["assuntos"]) or "—"
        titulo_card = f"{p['classe'] or 'Processo'} · {assuntos}"

        with st.expander(f"**{titulo_card}**"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Processo:** `{num}`")
                st.markdown(f"**Classe:** {p['classe'] or '—'}")
                st.markdown(f"**Assuntos:** {assuntos}")
            with c2:
                st.markdown(f"**Órgão julgador:** {p['orgaoJulgador'] or '—'}")
                st.markdown(f"**Último movimento:** {p['ultimoMovimento']} ({formatar_data(p['dataUltimoMovimento'])})")
                st.markdown(f"**Indexado em:** {formatar_data(p['ultimaAtualizacao'])}")

            st.markdown("---")

            # Verifica se já foi traduzido nesta sessão
            if num in st.session_state.traducoes:
                trad = st.session_state.traducoes[num]
                st.markdown(f"### {trad.get('titulo', '')}")
                st.markdown("**📝 Em linguagem simples**")
                st.write(trad.get("resumo_simples", "—"))
                st.markdown("**💡 Por que importa**")
                st.write(trad.get("por_que_importa", "—"))
                angulos = trad.get("angulos", [])
                if angulos:
                    st.markdown("**🎯 Ângulos de pauta**")
                    for a in angulos:
                        st.markdown(f"- {a}")
                glossario = trad.get("glossario", [])
                if glossario:
                    st.markdown("**📖 Glossário**")
                    for g in glossario:
                        st.markdown(f"**{g.get('termo', '')}**: {g.get('definicao', '')}")

                # Botão para enviar só este processo ao Telegram
                if st.button(f"📨 Enviar tradução ao Telegram", key=f"tg_{num}"):
                    trad_formatada = (
                        f"⚖️ <b>{trad.get('titulo', '')}</b>\n\n"
                        f"📁 <code>{num}</code>\n\n"
                        f"{trad.get('resumo_simples', '')}\n\n"
                        f"💡 <i>{trad.get('por_que_importa', '')}</i>"
                    )
                    ok = enviar_telegram(trad_formatada)
                    if ok:
                        st.success("Enviado ao Telegram!")
                    else:
                        st.warning("Erro ao enviar ao Telegram.")
            else:
                if st.button(f"✨ Traduzir com IA", key=f"trad_{num}"):
                    with st.spinner("Traduzindo com Gemini..."):
                        trad, erro = traduzir_processo(p)
                        if trad:
                            st.session_state.traducoes[num] = trad
                            st.rerun()
                        else:
                            st.error(erro)

st.markdown("---")
st.caption("Fonte: [DataJud/CNJ](https://datajud-wiki.cnj.jus.br) · tradução gerada por IA (Gemini)")
