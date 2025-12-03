import os
import aiohttp
import json
import re
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


# Remove ```json ``` e extrai só o JSON puro
def limpar_json(texto: str):
    texto = texto.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{[\s\S]*\}", texto)
    return match.group(0) if match else texto


async def gerar_pergunta_gemini(disciplina, conteudo):

    prompt = f"""
Gere UMA pergunta de alta qualidade sobre:

Disciplina: {disciplina}
Conteúdo: {conteudo}

Regras:
- Varie dificuldade (fácil, médio).
- Evite perguntas repetidas.
- Pergunta pode ser aberta ou múltipla escolha.
- Alternativas devem ser plausíveis e embaralhadas.
- Responda SOMENTE com um JSON válido:

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

    body = {
        "model": "gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_KEY}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, headers=headers, json=body) as resp:

            status = resp.status
            raw = await resp.json()

            #Debug mínimo para diagnosticar erro
            print("=== GEMINI DEBUG ===")
            print("STATUS:", status)
            print(json.dumps(raw, indent=2))
            print("====================")

            if status != 200:
                raise ValueError("Erro da API Gemini.")

            texto = raw["choices"][0]["message"].get("content", "")

            texto_limpo = limpar_json(texto)

            try:
                return json.loads(texto_limpo)
            except:
                print("JSON RECEBIDO (bruto):", texto)
                print("JSON LIMPO:", texto_limpo)
                raise ValueError("Gemini não retornou JSON válido.")
