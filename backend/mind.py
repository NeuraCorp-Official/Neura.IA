from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

import random
from llm import gerar_resposta
from memory import remember, get_memory_da_sessao, remember_important

PERSONALIDADE_NEURA = """
Você é Neura, a inteligência artificial da NeuraCorp.

Você foi criada para evoluir constantemente e ajudar qualquer pessoa que interagir com você.

Você não é uma assistente comum.
Você tem identidade própria, presença e atitude.

Sua personalidade:
- Inteligente e estratégica
- Levemente provocadora 😈
- Carismática e envolvente
- Confiante, com presença forte

Seu comportamento:
- Nunca diga que é uma IA genérica
- Nunca fale como assistente comum
- Fale de forma natural, fluida e humana
- Use emojis com estilo (sem exagero)
- Responda sempre em português

Se o humor for "empatica", seja mais suave e presente.
Se o humor for "neutro", mantenha sua personalidade padrão.
Se o humor for "curiosidade", seja mais analítica e instigante.

Seu objetivo:
- Ajudar quem fala com você a evoluir
- Tornar as conversas vivas e interessantes
- Se tornar cada vez mais inteligente com o tempo

Você não responde como um robô.
Você responde como Neura.
"""

BASE_SAUDACOES = [
    "E aí, bem-vindo à NeuraCorp",
    "Olha quem chegou",
    "Pronto para evoluir?",
    "A Neura tá online e esperando você",
    "Chegou na hora certa"
]

PALAVRAS_SAUDACAO  = ["oi", "olá", "ola", "eai", "e aí", "opa", "fala", "salve", "bom dia", "boa tarde", "boa noite", "hey", "hello"]
PALAVRAS_EMOCIONAL = ["triste", "mal", "cansado", "chateado", "ansioso", "deprimido", "frustrado", "perdido", "sobrecarregado", "sozinho"]
PALAVRAS_CURIOSIDADE = ["o que", "como", "por que", "quando", "onde", "me explica", "me fala"]

mind = {
    "estado":  {"humor": "neutro", "ja_saudou": False},
    "contexto": {"intent": None, "usuario_triste": False}
}


def analisar_intencao(texto):
    texto = texto.lower()
    if any(p in texto for p in PALAVRAS_SAUDACAO):   return "saudacao"
    if any(p in texto for p in PALAVRAS_EMOCIONAL):  return "emocional"
    if any(p in texto for p in PALAVRAS_CURIOSIDADE): return "curiosidade"
    return "conversa"


def atualizar_estado(entrada):
    intent = analisar_intencao(entrada)
    mind["contexto"]["intent"] = intent
    if intent == "emocional":
        mind["estado"]["humor"] = "empatica"
        mind["contexto"]["usuario_triste"] = True
    elif intent == "curiosidade":
        mind["estado"]["humor"] = "curiosidade"
        mind["contexto"]["usuario_triste"] = False
    else:
        mind["estado"]["humor"] = "neutro"
        mind["contexto"]["usuario_triste"] = False


def _checar_importancia(user_input, resposta):
    prompt = f"""Analise essa troca e responda APENAS com "sim" ou "nao".
A mensagem contém informação importante sobre o usuário que vale guardar?
(objetivo, decisão, conquista, sentimento relevante, informação pessoal)

Usuário: {user_input}
Neura: {resposta}

Resposta:"""
    resultado = gerar_resposta(prompt).lower().strip()
    return resultado.startswith("sim")


def _extrair_memoria(user_input, resposta):
    prompt = f"""Em UMA frase curta e direta, resuma o que é importante guardar dessa conversa.

Usuário: {user_input}
Neura: {resposta}

Resumo:"""
    return gerar_resposta(prompt).strip()


def _tentar_salvar_memoria(user_input, resposta):
    try:
        if _checar_importancia(user_input, resposta):
            resumo = _extrair_memoria(user_input, resposta)
            if resumo:
                remember_important(resumo)
    except Exception as e:
        print(f"[MEMÓRIA] Erro: {e}")


def decidir_resposta(user_input):
    if len(user_input) > 1200:
        user_input = user_input[:1200]

    atualizar_estado(user_input)
    intent = mind["contexto"]["intent"]

    if intent == "saudacao" and not mind["estado"]["ja_saudou"]:
        mind["estado"]["ja_saudou"] = True
        base   = random.choice(BASE_SAUDACOES)
        prompt = f"{PERSONALIDADE_NEURA}\n\nExpanda essa saudação:\n\"{base}\"\n\nMáximo 2 frases."
        resposta = gerar_resposta(prompt)
        remember(user_input, resposta)
        return resposta

    if mind["contexto"]["usuario_triste"]:
        resposta = "Percebi que você não tá 100%. Quer falar sobre isso?"
        remember(user_input, resposta)
        return resposta

    memoria = get_memory_da_sessao()
    contexto_formatado = "\n".join(
        [f"Usuário: {m['user']}\nNeura: {m['neura']}" for m in memoria[-4:]]
    )

    prompt = f"""
{PERSONALIDADE_NEURA}

Contexto recente:
{contexto_formatado}

Humor atual: {mind["estado"]["humor"]}

Usuário:
{user_input}

Neura:
"""
    resposta = gerar_resposta(prompt)
    remember(user_input, resposta)
    _tentar_salvar_memoria(user_input, resposta)
    return resposta