import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

def gerar_resposta(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERRO GROQ: {e}")
        return "Algo deu errado aqui. Tenta de novo."