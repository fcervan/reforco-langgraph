"""Aula 03 — Cadeias: o LLM que PEDE ferramenta (mas não a executa).

Ponte entre grafo puro (Aula 02) e agente (Aula 05):
- estado vira lista de MENSAGENS (quem falou + o quê);
- `bind_tools` dá ao LLM um "cardápio de funções": ele responde com texto
  OU com um JSON de intenção (`tool_calls`);
- SEM `add_messages`, cada nó apaga o histórico do anterior (overwrite);
  COM `MessagesState`, o histórico acumula.

Execute: python src/aula03_cadeias.py
Com GROQ_API_KEY usa Groq real (gpt-oss-20b); sem chave roda offline (Fake).
"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

MODELO = "openai/gpt-oss-20b"


def multiply(a: int, b: int) -> int:
    """Multiplica a por b. Args: a: primeiro int. b: segundo int."""
    return a * b


def soma(a: int, b: int) -> int:
    """Soma a e b. Args: a: primeiro int. b: segundo int."""
    return a + b


def get_llm():
    """Groq com cardápio [multiply, soma] — ou Fake offline determinístico."""
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print("AVISO: langchain_groq ausente -> seguirei no Fake offline.")
        else:
            # reasoning_effort="low": sem isso o gpt-oss gasta todos os tokens
            # raciocinando e devolve content vazio SEM tool_calls (Aula 01, seção 3.1).
            return ChatGroq(
                model=MODELO, temperature=0, reasoning_effort="low"
            ).bind_tools([multiply, soma])
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    fake = AIMessage(
        content="",
        tool_calls=[{"name": "multiply", "args": {"a": 3, "b": 4}, "id": "call_1", "type": "tool_call"}],
    )
    return FakeMessagesListChatModel(responses=[fake])


def no_atendente(state: MessagesState) -> dict[str, Any]:
    llm = get_llm()
    resposta = llm.invoke(state["messages"])
    return {"messages": [resposta]}  # add_messages ANEXA; sem reducer, sobrescreveria


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("no_atendente", no_atendente)
    builder.add_edge(START, "no_atendente")
    builder.add_edge("no_atendente", END)
    return builder.compile()


def demo_pergunta(graph, pergunta: str) -> None:
    out = graph.invoke({"messages": [HumanMessage(content=pergunta)]})
    ultima: AIMessage = out["messages"][-1]
    print(f"P: {pergunta}")
    print(f"   content: {ultima.content!r}")
    print(f"   tool_calls: {ultima.tool_calls}")
    if ultima.tool_calls:
        print("   -> o LLM PEDIU a tool, mas NINGUÉM executou (isso é a Aula 04).")


def demo_problema_overwrite() -> None:
    """SEM reducer, o 2º nó apaga o histórico do 1º."""
    from typing import TypedDict

    class SemReducer(TypedDict):
        messages: list

    def no_pergunta(state: SemReducer) -> dict:
        return {"messages": [HumanMessage(content="pergunta do usuário")]}

    def no_resposta(state: SemReducer) -> dict:
        return {"messages": [AIMessage(content="resposta do bot")]}

    builder = StateGraph(SemReducer)
    builder.add_node("n1", no_pergunta)
    builder.add_node("n2", no_resposta)
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n2", END)
    out = builder.compile().invoke({"messages": []})
    print("SEM reducer (histórico PERDIDO):")
    for m in out["messages"]:
        print(f"   [{type(m).__name__}] {m.content!r}")


def demo_com_reducer() -> None:
    """COM MessagesState, o histórico acumula."""

    def no_pergunta(state: MessagesState) -> dict:
        return {"messages": [HumanMessage(content="pergunta do usuário")]}

    def no_resposta(state: MessagesState) -> dict:
        return {"messages": [AIMessage(content="resposta do bot")]}

    builder = StateGraph(MessagesState)
    builder.add_node("n1", no_pergunta)
    builder.add_node("n2", no_resposta)
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n2", END)
    out = builder.compile().invoke({"messages": []})
    print("COM reducer (histórico PRESERVADO):")
    for m in out["messages"]:
        print(f"   [{type(m).__name__}] {m.content!r}")


def main() -> None:
    graph = build_graph()
    print("=== o LLM pede ferramenta (não executa) ===")
    demo_pergunta(graph, "Quanto é 3 vezes 4?")
    print("\n=== o problema do overwrite ===")
    demo_problema_overwrite()
    print("\n=== a solução: MessagesState ===")
    demo_com_reducer()


if __name__ == "__main__":
    main()


# SITUAÇÕES P/ VOCÊ TENTAR:
# 1. Pergunte "oi, tudo bem?" e observe tool_calls vazio (resposta direta).
#    (Offline: o Fake sempre devolve o mesmo tool_call — troque-o no get_llm.)
# 2. Com a chave Groq, pergunte "some 10 com 5" e confira se o LLM escolhe `soma`.
# 3. Adicione uma 3ª tool `dividir(a, b)` e veja o cardápio crescer.
