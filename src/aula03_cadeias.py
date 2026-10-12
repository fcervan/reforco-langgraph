"""Aula 3 — Falando de Cadeias: LLM que detecta intenção de usar tool.

Ponte: sem grafo o LLM só responde; com bind_tools ele pode
responder OU pedir uma ferramenta (tool_calls). Ainda NÃO executa.

Execute: python src/aula03_cadeias.py
Com GROQ_API_KEY no .env usa Groq; sem chave roda offline (Fake).
"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()


def multiply(a: int, b: int) -> int:
    """Multiplica dois inteiros (nossa primeira tool)."""
    return a * b


def get_llm():
    """Groq se houver chave, senão Fake offline determinístico."""
    if os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq

        return ChatGroq(model="openai/gpt-oss-20b", temperature=0).bind_tools([multiply])
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    fake = AIMessage(
        content="",
        tool_calls=[{"name": "multiply", "args": {"a": 3, "b": 4}, "id": "call_1", "type": "tool_call"}],
    )
    return FakeMessagesListChatModel(responses=[fake])


def tool_calling_llm(state: MessagesState) -> dict[str, Any]:
    llm = get_llm()
    resposta = llm.invoke(state["messages"])
    return {"messages": [resposta]}


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_edge(START, "tool_calling_llm")
    builder.add_edge("tool_calling_llm", END)
    return builder.compile()


def main() -> None:
    graph = build_graph()
    out = graph.invoke({"messages": [HumanMessage(content="Quanto é 3 vezes 4?")]})
    ultima: AIMessage = out["messages"][-1]
    print("content:", repr(ultima.content))
    print("tool_calls:", ultima.tool_calls)
    if ultima.tool_calls:
        print("-> o LLM PEDIU a tool, mas ninguém executou (isso é a Aula 4).")
    else:
        print("-> resposta direta, sem tool (tente pergunta de conta p/ ver tool_calls).")


if __name__ == "__main__":
    main()


# SITUAÇÃO P/ VOCÊ TENTAR:
# 1. Pergunte "oi, tudo bem?" e observe tool_calls vazio (offline: troque o Fake).
# 2. Adicione uma 2a tool `soma(a, b)` no bind_tools e veja o LLM escolher entre elas.
