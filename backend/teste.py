from dotenv import load_dotenv
from pathlib import Path
import os
from groq import Groq

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

resposta = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Fala oi em português"}],
    max_tokens=100
)

print(resposta.choices[0].message.content)