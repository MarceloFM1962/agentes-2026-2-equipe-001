"""
Cliente único de LLM da disciplina.

Todo o projeto conversa com o modelo por aqui. Nenhum outro arquivo deve
importar a biblioteca do provedor diretamente.

Por quê: trocar de provedor (Gemini → Groq → Ollama) passa a ser editar o .env,
não reescrever o código. Isso é conteúdo da disciplina, não conveniência —
desacoplamento de fornecedor é decisão de arquitetura real.

Uso:
    from llm import conversar
    print(conversar("Explique o que é um agente em uma frase."))
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_BASE_URL = os.getenv("LLM_BASE_URL")
_MODELO = os.getenv("LLM_MODEL")
_CHAVE = os.getenv("LLM_API_KEY")

if not (_BASE_URL and _MODELO and _CHAVE):
    raise RuntimeError(
        "Configuração incompleta. Copie o .env.example para .env e preencha "
        "LLM_BASE_URL, LLM_MODEL e LLM_API_KEY."
    )

if _CHAVE.startswith("cole-sua-chave"):
    raise RuntimeError(
        "A chave no .env ainda é o texto de exemplo. Cole sua chave de verdade."
    )

cliente = OpenAI(base_url=_BASE_URL, api_key=_CHAVE)

MAX_ITERACOES = int(os.getenv("AGENTE_MAX_ITERACOES", "8"))
MAX_TENTATIVAS_429 = int(os.getenv("AGENTE_MAX_TENTATIVAS_429", "5"))


def conversar(
    mensagem_do_usuario: str,
    instrucao_de_sistema: str | None = None,
    temperatura: float = 0.0,
) -> str:
    """Envia uma mensagem ao modelo e devolve o texto da resposta.

    A partir do Encontro 3 esta função ganha repetição com backoff para o
    erro 429 (limite de taxa do tier gratuito) e suporte a ferramentas.
    """
    mensagens: list[dict[str, str]] = []
    if instrucao_de_sistema:
        mensagens.append({"role": "system", "content": instrucao_de_sistema})
    mensagens.append({"role": "user", "content": mensagem_do_usuario})

    resposta = cliente.chat.completions.create(
        model=_MODELO,
        messages=mensagens,
        temperature=temperatura,
    )
    return resposta.choices[0].message.content or ""


def descrever_configuracao() -> str:
    """Mostra o provedor em uso, sem revelar a chave. Útil para depurar."""
    return f"provedor={_BASE_URL} · modelo={_MODELO} · chave=...{_CHAVE[-4:]}"
