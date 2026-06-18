import os
import json
from google import genai

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

PROMPT_SISTEMA = """Você é um analista de notícias de direito e tecnologia. Sua missão é
traduzir processos judiciais do STJ em sugestões de pauta jornalística acessíveis ao
público geral, eliminando o juridiquês.

Para cada processo recebido, retorne um objeto JSON com:
- "titulo": título de pauta em linguagem simples, chamativo mas factual
- "resumo_simples": 2-3 frases explicando o que está em jogo, sem juridiquês
- "por_que_importa": 1-2 frases sobre o impacto para o cidadão comum
- "angulos": lista de 2-3 sugestões de ângulo de reportagem
- "glossario": lista de objetos {"termo": ..., "definicao": ...} para os termos
  jurídicos usados (classe processual, tipo de movimento, etc.)

Mantenha os campos originais "numeroProcesso", "classe", "orgaoJulgador",
"assuntos", "ultimoMovimento" e "dataUltimoMovimento" no objeto de saída.

Responda APENAS com um array JSON válido, sem texto adicional, sem markdown,
sem ```json."""


def gerar_pautas(processos):
    if not processos:
        return []

    entrada = json.dumps(processos, ensure_ascii=False, indent=2)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{PROMPT_SISTEMA}\n\nProcessos para análise:\n\n{entrada}"
    )

    texto = response.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    try:
        resultado = json.loads(texto)
        return resultado
    except json.JSONDecodeError:
        print("Erro ao parsear resposta do Gemini:")
        print(texto)
        return []


if __name__ == "__main__":
    with open("pautas.json", "r", encoding="utf-8") as f:
        processos = json.load(f)

    if not processos:
        print("Nenhum processo para traduzir.")
        with open("pautas_traduzidas.json", "w", encoding="utf-8") as f:
            json.dump([], f)
    else:
        pautas = gerar_pautas(processos)
        print(f"{len(pautas)} pautas traduzidas geradas")
        with open("pautas_traduzidas.json", "w", encoding="utf-8") as f:
            json.dump(pautas, f, ensure_ascii=False, indent=2)
