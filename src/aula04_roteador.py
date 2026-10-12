"""Aula 4 — Roteadores: LLM decide, ToolNode executa.

Evolução da Aula 3: se o LLM pedir tool -> vai p/ "tools" e executa;
senão -> END. Usa os pré-construídos ToolNode + tools_condition.

Execute: python src/aula04_roteador.py
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


def multiply(a: int, b: int) -> int:
    """Multiplica dois inteiros."""
    return a * b


def get_llm_com_tools(conta: bool = True):
    """Fake offline (conta=True retorna tool_call) ou Groq com chave."""
    if os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq

        return ChatGroq(model="openai/gpt-oss-20b", temperature=0).bind_tools([multiply])
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    if conta:
        resp = AIMessage(
            content="",
            tool_calls=[
                {"name": "multiply", "args": {"a": 3, "b": 4}, "id": "call_1", "type": "tool_call"}
            ],
        )
    else:
        resp = AIMessage(content="Olá! Como posso ajudar?", tool_calls=[])
    return FakeMessagesListChatModel(responses=[resp])


def make_assistant(conta: bool = True):
    llm = get_llm_com_tools(conta)

    def assistant(state: MessagesState) -> dict:
        return {"messages": [llm.invoke(state["messages"])]}

    return assistant


def build_graph(conta: bool = True):
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(conta))
    builder.add_node("tools", ToolNode([multiply]))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", END)
    return builder.compile()


def mostrar(pergunta: str, conta: bool) -> None:
    graph = build_graph(conta)
    out = graph.invoke({"messages": [HumanMessage(content=pergunta)]})
    for m in out["messages"]:
        print(f"  [{type(m).__name__}] {m.content!r} {getattr(m, 'tool_calls', '')}")
    print()


def main() -> None:
    print("Caso 1 — pergunta de conta (esperado: assistant -> tools -> ToolMessage):")
    mostrar("Quanto é 3 vezes 4?", conta=True)
    print("Caso 2 — conversa simples (esperado: assistant -> END, sem tools):")
    mostrar("Oi, tudo bem?", conta=False)


if __name__ == "__main__":
    main()


# SITUAÇÃO P/ VOCÊ TENTAR (porteiro):
# Adicione a tool `soma(a,b)`. Pergunte "some 2+5" e confira se o
# tools_condition mandou para "tools" e o ToolMessage trouxe 7.
