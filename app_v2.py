import streamlit as st
import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")


# ── Funções auxiliares ─────────────────────────────────────────────────────────

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
        prompt = f"""Você é o "JurisTradutor STF". Traduza este processo do TJRJ para linguagem simples.

Processo:
{json.dumps(processo, ensure_ascii=False, indent=2)}

Retorne APENAS um objeto JSON com:
- "titulo": título em linguagem simples
- "resumo_simples": 2-3 frases sem juridiquês
- "por_que_importa": impacto para o cidadão (1-2 frases)
- "angulos": lista de 2-3 sugestões de ângulo de reportagem
- "glossario": lista de objetos {{"termo": ..., "definicao": ...}}

Sem markdown, sem texto extra, só o JSON."""

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
        return False, "Secrets do Telegram não configurados."
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    })
    return resp.status_code == 200, resp.text


def montar_html_email(processos_selecionados, traducoes):
    cards = ""
    for num in processos_selecionados:
        p = next((x for x in st.session_state.processos if x["numeroProcesso"] == num), None)
        if not p:
            continue
        trad = traducoes.get(num)
        assuntos = ", ".join(p["assuntos"]) or "—"

        if trad:
            conteudo_trad = f"""
            <div style="margin-top:12px;padding:12px;background:#f0f7ff;border-radius:6px;">
                <h3 style="margin:0 0 8px;font-size:16px;color:#185FA5">{trad.get('titulo','')}</h3>
                <p style="margin:0 0 8px;font-size:13px;color:#333">{trad.get('resumo_simples','')}</p>
                <p style="margin:0 0 8px;font-size:13px;color:#555"><i>💡 {trad.get('por_que_importa','')}</i></p>
                {"<ul style='margin:0 0 8px;padding-left:18px'>" + "".join(f"<li style='font-size:13px;color:#333'>{a}</li>" for a in trad.get('angulos',[])) + "</ul>" if trad.get('angulos') else ""}
                {"<div style='margin-top:8px'><b style='font-size:12px;color:#888;text-transform:uppercase;letter-spacing:.05em'>Glossário</b>" + "".join(f"<p style='font-size:12px;margin:4px 0'><b>{g.get('termo','')}</b>: {g.get('definicao','')}</p>" for g in trad.get('glossario',[])) + "</div>" if trad.get('glossario') else ""}
            </div>"""
        else:
            conteudo_trad = "<p style='font-size:12px;color:#888;font-style:italic'>Tradução não solicitada para este processo.</p>"

        cards += f"""
        <div style="margin-bottom:20px;padding:16px;border:1px solid #e0e0e0;border-radius:10px;background:#fff">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
                <span style="font-size:11px;background:#EAF3DE;color:#3B6D11;padding:3px 9px;border-radius:20px;font-weight:600">{p.get('classe','Processo')}</span>
                <span style="font-size:11px;font-family:monospace;background:#f5f5f5;padding:2px 7px;border-radius:4px;color:#555">{num}</span>
            </div>
            <p style="margin:8px 0 4px;font-size:13px;color:#555">📌 <b>Assuntos:</b> {assuntos}</p>
            <p style="margin:4px 0;font-size:13px;color:#555">👤 {p.get('orgaoJulgador','—')}</p>
            <p style="margin:4px 0;font-size:13px;color:#555">🔄 {p.get('ultimoMovimento','—')} ({formatar_data(p.get('dataUltimoMovimento'))})</p>
            {conteudo_trad}
        </div>"""

    return f"""
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:640px;margin:0 auto;padding:20px;background:#f9f9f9">
        <div style="background:#fff;border-radius:12px;padding:24px;border:1px solid #e0e0e0">
            <h1 style="font-size:20px;font-weight:600;margin:0 0 4px">⚖️ Monitor TJRJ</h1>
            <p style="font-size:13px;color:#888;margin:0 0 20px">Processos selecionados · Fonte: DataJud/CNJ · Tradução: Gemini IA</p>
            {cards}
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0">
            <p style="font-size:11px;color:#aaa;text-align:center">Fonte: DataJud/CNJ · tradução gerada por IA (Gemini)</p>
        </div>
    </body>
    </html>"""


def enviar_email(destinatario, html, assunto="Monitor TJRJ — Processos Selecionados"):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False, "Secrets do Gmail não configurados."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = GMAIL_USER
        msg["To"] = destinatario
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)


# ── Interface ──────────────────────────────────────────────────────────────────

st.title("🔍 Busca de Processos — TJRJ")
st.caption("Busca direta na API DataJud/CNJ · Até 50 resultados · Tradução sob demanda · Envio por e-mail e Telegram")

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
    enviar_tg = st.button("📨 Buscar e enviar ao Telegram", use_container_width=True)

# Inicializa estado da sessão
if "traducoes" not in st.session_state:
    st.session_state.traducoes = {}
if "selecionados" not in st.session_state:
    st.session_state.selecionados = set()

if (buscar or enviar_tg) and termo.strip():
    with st.spinner(f"Buscando processos sobre '{termo}'..."):
        try:
            resultado = buscar_por_assunto(termo.strip(), tamanho=50)
            processos = extrair_processos(resultado)
            total = resultado.get("hits", {}).get("total", {}).get("value", 0)
            st.session_state.processos = processos
            st.session_state.total = total
            st.session_state.termo = termo.strip()
            st.session_state.traducoes = {}
            st.session_state.selecionados = set()

            if enviar_tg:
                if not processos:
                    texto_tg = f"🔍 <b>Busca: {termo}</b>\n\nNenhum processo encontrado."
                else:
                    linhas = [f"🔍 <b>Busca: {termo}</b> — {len(processos)} resultado(s)\n"]
                    for i, p in enumerate(processos[:10], 1):
                        assuntos = ", ".join(p["assuntos"][:2])
                        linhas.append(
                            f"<b>{i}. {p['classe'] or 'Processo'}</b>\n"
                            f"📁 <code>{p['numeroProcesso']}</code>\n"
                            f"📌 {assuntos}\n"
                            f"🔄 {p['ultimoMovimento']} ({formatar_data(p['dataUltimoMovimento'])})\n"
                        )
                    if len(processos) > 10:
                        linhas.append(f"<i>... e mais {len(processos) - 10} resultados.</i>")
                    texto_tg = "\n".join(linhas)
                ok, _ = enviar_telegram(texto_tg)
                if ok:
                    st.info("📨 Resultado enviado ao Telegram!")
                else:
                    st.warning("Erro ao enviar ao Telegram. Verifique os secrets.")

        except requests.exceptions.ConnectTimeout:
            st.error("Timeout ao conectar com o DataJud. Tente novamente.")
            st.stop()
        except Exception as e:
            st.error(f"Erro na busca: {type(e).__name__}: {e}")
            st.stop()

elif (buscar or enviar_tg) and not termo.strip():
    st.warning("Digite um termo de busca antes de pesquisar.")

# ── Resultados ─────────────────────────────────────────────────────────────────
if "processos" in st.session_state and st.session_state.processos is not None:
    processos = st.session_state.processos
    total = st.session_state.total
    termo_atual = st.session_state.termo

    st.success(f"**{len(processos)} processos** para '{termo_atual}' (total na base: {total})")

    # Painel de envio por e-mail (aparece quando há selecionados)
    if st.session_state.selecionados:
        with st.container():
            st.markdown("---")
            st.markdown(f"**{len(st.session_state.selecionados)} processo(s) selecionado(s)**")
            destinatario = st.text_input("Enviar para o e-mail:", placeholder="exemplo@email.com", key="email_input")
            col_email, col_tg_sel = st.columns(2)
            with col_email:
                if st.button("📧 Enviar por e-mail", type="primary", use_container_width=True):
                    if destinatario.strip():
                        html = montar_html_email(list(st.session_state.selecionados), st.session_state.traducoes)
                        ok, erro = enviar_email(destinatario.strip(), html)
                        if ok:
                            st.success(f"✅ E-mail enviado para {destinatario}!")
                        else:
                            st.error(f"Erro ao enviar: {erro}")
                    else:
                        st.warning("Digite um e-mail de destino.")
            with col_tg_sel:
                if st.button("📨 Enviar selecionados ao Telegram", use_container_width=True):
                    linhas = [f"📋 <b>Processos selecionados ({len(st.session_state.selecionados)})</b>\n"]
                    for num in st.session_state.selecionados:
                        p = next((x for x in processos if x["numeroProcesso"] == num), None)
                        trad = st.session_state.traducoes.get(num)
                        if p:
                            if trad:
                                linhas.append(
                                    f"⚖️ <b>{trad.get('titulo','')}</b>\n"
                                    f"📁 <code>{num}</code>\n"
                                    f"{trad.get('resumo_simples','')}\n"
                                    f"💡 <i>{trad.get('por_que_importa','')}</i>\n"
                                )
                            else:
                                assuntos = ", ".join(p["assuntos"][:2])
                                linhas.append(
                                    f"<b>{p['classe']}</b>\n"
                                    f"📁 <code>{num}</code>\n"
                                    f"📌 {assuntos}\n"
                                )
                    ok, _ = enviar_telegram("\n".join(linhas))
                    if ok:
                        st.success("📨 Enviado ao Telegram!")
                    else:
                        st.warning("Erro ao enviar ao Telegram.")
            st.markdown("---")

    # Lista de processos com checkboxes
    for i, p in enumerate(processos):
        num = p["numeroProcesso"]
        assuntos = ", ".join(p["assuntos"]) or "—"
        titulo_card = f"{p['classe'] or 'Processo'} · {assuntos}"

        col_cb, col_card = st.columns([0.05, 0.95])
        with col_cb:
            selecionado = st.checkbox("", key=f"cb_{num}", value=(num in st.session_state.selecionados))
            if selecionado:
                st.session_state.selecionados.add(num)
            else:
                st.session_state.selecionados.discard(num)

        with col_card:
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
