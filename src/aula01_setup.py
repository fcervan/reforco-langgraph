"""Aula 01 — Setup: do zero à primeira chamada LLM.

Com GROQ_API_KEY no .env usa Groq real; sem chave roda offline (Fake).
Execute: python src/aula01_setup.py
"""

import getpass
import os

from dotenv import load_dotenv

load_dotenv()

MODELO = "openai/gpt-oss-20b"


def _set_env(var: str) -> None:
    """Pede a chave via digitação oculta se ela ainda não existir (nada é salvo no repo)."""
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


def tem_chave() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def get_llm(temperature: float = 0, reasoning_effort: str = "low"):
    """Retorna (llm, origem) onde origem é 'groq' ou 'fake'.

    `reasoning_effort` controla o ORÇAMENTO de tokens que o modelo gasta
    raciocinando antes de responder (low/medium/high; não existe "off").
    Modelos como `openai/gpt-oss-20b` primeiro raciocinam e só depois
    escrevem: com esforço alto eles gastam todos os tokens de conclusão
    pensando, estouram em `finish_reason: length` e devolvem `content`
    VAZIO (o raciocínio fica em `additional_kwargs['reasoning_content']`).
    Para estudos, tools e agentes -> use "low": resposta rápida e previsível.
    """
    if tem_chave():
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print(
                "AVISO: langchain_groq ausente -> instale com "
                "`pip install langchain-groq` (ou %pip install no Colab)."
            )
        else:
            return (
                ChatGroq(
                    model=MODELO, temperature=temperature, reasoning_effort=reasoning_effort
                ),
                "groq",
            )
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage

    print("AVISO: modo Fake offline (mecânica igual, texto simulado).")
    fake = FakeMessagesListChatModel(
        responses=[AIMessage(content="Olá! Sou uma resposta simulada para estudo offline.")]
    )
    return fake, "fake"


def main() -> None:
    llm, origem = get_llm()
    print(f"origem: {origem} | modelo: {MODELO}\n")

    resposta = llm.invoke("Como vai você? Responda em uma frase.")
    print("invoke ->", repr(resposta.content))
    print("tipo   ->", type(resposta).__name__)

    print("\nstream -> ", end="")
    for pedaco in llm.stream("Diga 'um dois três' e pare."):
        print(pedaco.content, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
