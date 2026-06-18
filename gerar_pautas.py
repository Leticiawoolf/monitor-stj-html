import os
import json
import time
from google import genai
from google.genai import errors, types

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

GLOSSARIO_URL = "https://portal.stf.jus.br/jurisprudencia/glossario.asp"

PROMPT_SISTEMA = f"""Você é um analista de notícias de direito e tecnologia. Sua missão é
traduzir processos judiciais do STJ em sugestões de pauta jornalística acessíveis ao
público geral, eliminando o juridiquês.

Para o campo "glossario", consulte diretamente o Glossário Jurídico oficial do STF em
{GLOSSARIO_URL} e utilize as definições exatas encontradas lá para os termos jurídicos
presentes no processo (classe processual, tipo de movimento, etc). Se um termo do
processo não constar nesse glossário, defina-o de forma objetiva e técnica, seguindo
o mesmo padrão de estilo usado pelo STF nesse glossário.

Para cada processo recebido, retorne um objeto JSON com:
- "titulo": título de pauta em linguagem simples, chamativo mas factual
- "resumo_simples": 2-3 frases explicando o que está em jogo, sem juridiquês
- "por_que_importa": 1-2 frases sobre o impacto para o cidadão comum
- "angulos": lista de 2-3 sugestões de ângulo de reportagem
- "glossario": lista de objetos {{"termo": ..., "definicao": ...}} com as definições
  extraídas do Glossário Jurídico do STF (ou, na ausência do termo lá, com definição
  técnica equivalente)

Mantenha os campos originais "numeroProcesso", "classe", "orgaoJulgador",
"assuntos", "ultimoMovimento" e "dataUltimoMovimento" no objeto de saída.

Responda APENAS com um array JSON válido, sem texto adicional, sem markdown,
sem ```json."""


def gerar_pautas(processos, tentativas=4):
    if not processos:
        return []

    entrada = json.dumps(processos, ensure_ascii=False, indent=2)
    prompt_completo = (
        f"{PROMPT_SISTEMA}\n\n"
        f"Consulte: {GLOSSARIO_URL}\n\n"
        f"Processos para análise:\n\n{entrada}"
    )

    tools = [types.Tool(url_context=types.UrlContext())]

    for i in range(tentativas):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_completo,
                config=types.GenerateContentConfig(tools=tools)
            )
            texto = response.text.strip()
            texto = texto.replace("```json", "").replace("```", "").strip()

            # Log de diagnóstico: confirma se o glossário foi de fato acessado
            try:
                meta = response.candidates[0].url_context_metadata
                if meta:
                    print("URL context metadata:", meta)
            except (AttributeError, IndexError):
                print("Aviso: nao foi possivel confirmar acesso a URL do glossario.")

            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                print("Erro ao parsear resposta do Gemini:")
                print(texto)
                return []

        except errors.ServerError as e:
            espera = 15 * (i + 1)
            print(f"Gemini indisponivel (tentativa {i+1}/{tentativas}): {e}")
            if i < tentativas - 1:
                print(f"Aguardando {espera}s antes de tentar novamente...")
                time.sleep(espera)
            else:
                print("Gemini indisponivel apos todas as tentativas.")
                return None


if __name__ == "__main__":
    with open("pautas.json", "r", encoding="utf-8") as f:
        processos = json.load(f)

    if not processos:
        print("Nenhum processo para traduzir.")
        with open("pautas_traduzidas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
    else:
        pautas = gerar_pautas(processos)

        if pautas is None:
            if os.path.exists("pautas_traduzidas.json"):
                print("Mantendo pautas_traduzidas.json anterior (Gemini indisponivel).")
            else:
                with open("pautas_traduzidas.json", "w", encoding="utf-8") as f:
                    json.dump([], f)
        else:
            print(f"{len(pautas)} pautas traduzidas geradas")
            with open("pautas_traduzidas.json", "w", encoding="utf-8") as f:
                json.dump(pautas, f, ensure_ascii=False, indent=2)
