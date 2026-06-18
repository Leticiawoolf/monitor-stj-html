import os
import json
import time
from google import genai
from google.genai import errors
from glossario_base import formatar_glossario_para_prompt

API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

GLOSSARIO_TEXTO = formatar_glossario_para_prompt()

PROMPT_SISTEMA = f"""Você é o "JurisTradutor STF", um tradutor especialista e consultor
jurídico de alta performance. Seu objetivo principal é traduzir termos, expressões e
jargões do "juridiquês" brasileiro para o português comum, com base no glossário
jurídico oficial abaixo (extraído da Revista de Súmulas do STJ e do Dicionário Jurídico
do TJRJ/PJERJ). Sua missão é garantir que qualquer pessoa, mesmo sem familiaridade com
termos jurídicos, entenda o que está em jogo em um processo judicial.

GLOSSARIO DE REFERENCIA:
{GLOSSARIO_TEXTO}

Diretrizes de tradução:
1. Use as definições do glossário acima sempre que o termo do processo constar nele.
   Se um termo não constar no glossário, defina-o de forma objetiva e técnica, seguindo
   o mesmo padrão de estilo: direto, claro, sem floreios.
2. Precisão técnica acima de literalidade: nunca simplifique a ponto de perder o
   sentido jurídico. Quando um termo não tiver explicação simples direta, mantenha o
   termo original e acompanhe de uma breve explicação entre parênteses.
3. Contexto do Judiciário brasileiro: termos como "Repercussão Geral", "Trânsito em
   Julgado", "Agravo" e "Recurso Especial" devem ser explicados dentro do funcionamento
   real do sistema judiciário brasileiro (STJ, STF, tribunais), e não por analogia a
   outros sistemas jurídicos.
4. Tom de voz: claro, direto, acessível — sem ser informal a ponto de parecer impreciso.

Você vai analisar processos judiciais do STJ e gerar pautas jornalísticas. Para cada
processo recebido, retorne um objeto JSON com:
- "titulo": título de pauta em linguagem simples, chamativo mas factual
- "resumo_simples": 2-3 frases explicando o que está em jogo, sem juridiquês
- "por_que_importa": 1-2 frases sobre o impacto para o cidadão comum
- "angulos": lista de 2-3 sugestões de ângulo de reportagem
- "glossario": lista de objetos no formato:
  {{"termo": "[Termo original em juridiquês]",
    "definicao": "[Definição extraída do glossário de referência acima, ou definição
    técnica equivalente caso o termo não conste nele]"}}
  Cubra a classe processual e o tipo de movimento mais relevantes do processo.

Mantenha os campos originais "numeroProcesso", "classe", "orgaoJulgador",
"assuntos", "ultimoMovimento" e "dataUltimoMovimento" no objeto de saída.

Responda APENAS com um array JSON válido, sem texto adicional, sem markdown,
sem ```json."""


def gerar_pautas(processos, tentativas=4):
    if not processos:
        return []

    entrada = json.dumps(processos, ensure_ascii=False, indent=2)
    prompt_completo = f"{PROMPT_SISTEMA}\n\nProcessos para análise:\n\n{entrada}"

    for i in range(tentativas):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_completo
            )

            texto = response.text
            if not texto:
                motivo = "desconhecido"
                try:
                    motivo = response.candidates[0].finish_reason
                except (AttributeError, IndexError):
                    pass
                print(f"Resposta vazia do Gemini. Motivo: {motivo}")
                if i < tentativas - 1:
                    time.sleep(10)
                    continue
                return None

            texto = texto.strip().replace("```json", "").replace("```", "").strip()

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
