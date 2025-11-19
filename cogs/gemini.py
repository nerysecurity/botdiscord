import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_API_URL")

async def gerar_pergunta_gemini(disciplina, conteudo):
    prompt = f"""
Gere uma pergunta de quiz sobre a disciplina: {disciplina}
e o conteúdo específico: {conteudo}.

A pergunta pode ser:
- do tipo 'aberta'
- do tipo 'multipla' (5 alternativas A,B,C,D,E)

Escolha aleatoriamente.

Responda EXATAMENTE no seguinte JSON:

{{
  "tipo": "aberta" ou "multipla",
  "pergunta": "texto",
  "alternativas": {{
    "A": "...",
    "B": "...",
    "C": "...",
    "D": "...",
    "E": "..."
  }} ou null,
  "correta": "texto ou letra"
}}
"""

    # Corpo da requisição no formato da API Gemini 2.5 Flash
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, headers=headers, json=body) as response:
            resposta = await response.json()

            # DEBUG opcional para ver raw da IA
            print("RAW GEMINI:", resposta)

            # A resposta vem assim:
            # resposta["candidates"][0]["content"]["parts"][0]["text"]
            try:
                texto = resposta["candidates"][0]["content"]["parts"][0]["text"]
            except:
                raise ValueError("A IA não retornou o formato esperado.")

            # Agora tentar transformar o texto em JSON
            try:
                return json.loads(texto)
            except:
                # Tentar extrair JSON manualmente
                import re
                match = re.search(r"\{.*\}", texto, flags=re.S)
                if match:
                    return json.loads(match.group(0))
                else:
                    raise ValueError("O Gemini não retornou um JSON válido.")
