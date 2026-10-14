"""Aula 04 — Roteadores: o LLM decide, o ToolNode executa.

Evolução da Aula 03: agora existe quem EXECUTE o pedido.
- `tools_condition` é o porteiro: tem `tool_calls`? vai para "tools";
  senão, vai para `END` (na prática, devolve "tools" ou "__end__").
- `ToolNode([multiply, soma])` executa a função Python de verdade e anexa
  o resultado como `ToolMessage` (com `name` e `tool_call_id` do pedido).
- Sem ciclo de volta (isso é a Aula 05): após `tools`, o grafo encerra.

Execute: python src/aula04_roteador.py
Com GROQ_API_KEY usa Groq real (gpt-oss-20b); sem chave roda offline (Fake).
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

MODELO = "openai/gpt-oss-20b"


def multiply(a: int, b: int) -> int:
    """Multiplica a por b."""
    return a * b


def soma(a: int, b: int) -> int:
    """Soma a e b."""
    return a + b


def divide(a: int, b: int) -> float:
    """Divide a por b."""
    return a / b


TOOLS = [multiply, soma]


def get_llm_com_tools(conta: bool = True):
    """Groq com cardápio [multiply, soma] — ou Fake offline determinístico."""
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print("AVISO: langchain_groq ausente -> seguirei no Fake offline.")
        else:
            # reasoning_effort="low": sem isso o gpt-oss nunca emite tool_calls
            # e o tools_condition mandaria tudo para END (Aula 01, seção 3.1).
            return ChatGroq(
                model=MODELO, temperature=0, reasoning_effort="low"
            ).bind_tools(TOOLS)
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
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", END)
    return builder.compile()


def mostrar(pergunta: str, conta: bool = True) -> None:
    graph = build_graph(conta)
    out = graph.invoke({"messages": [HumanMessage(content=pergunta)]})
    print(f"P: {pergunta}")
    for m in out["messages"]:
        extra = ""
        if type(m).__name__ == "ToolMessage":
            extra = f" (name={m.name}, id={m.tool_call_id})"
        print(f"   [{type(m).__name__}]{extra} {m.content!r}")
    print()


def demo_tool_fora_da_lista() -> None:
    """LLM pede tool que não está no ToolNode: vira ToolMessage de ERRO (não quebra)."""
    pedido = AIMessage(
        content="",
        tool_calls=[{"name": "fantasma", "args": {}, "id": "c1", "type": "tool_call"}],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    out = builder.compile().invoke({"messages": [pedido]})
    for m in out["messages"][1:]:
        print(f"   [{type(m).__name__}] {m.content!r}")


def demo_erro_na_tool() -> None:
    """Tool que explode (1/0): a exceção PROPAGA e quebra a execução."""
    pedido = AIMessage(
        content="",
        tool_calls=[{"name": "divide", "args": {"a": 1, "b": 0}, "id": "c2", "type": "tool_call"}],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode([divide]))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    try:
        builder.compile().invoke({"messages": [pedido]})
    except ZeroDivisionError as erro:
        print(f"   ZeroDivisionError propagado: {erro}")
        print("   -> valide args ANTES de expor a tool (ou trate dentro dela).")


def demo_dois_pedidos() -> None:
    """Dois tool_calls de uma vez: um ToolMessage para cada."""
    pedido = AIMessage(
        content="",
        tool_calls=[
            {"name": "multiply", "args": {"a": 2, "b": 3}, "id": "c3", "type": "tool_call"},
            {"name": "multiply", "args": {"a": 4, "b": 5}, "id": "c4", "type": "tool_call"},
        ],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    out = builder.compile().invoke({"messages": [pedido]})
    for m in out["messages"][1:]:
        print(f"   [{type(m).__name__} id={m.tool_call_id}] {m.content!r}")


def main() -> None:
    print("=== caso 1: conta -> assistant -> tools -> ToolMessage ===")
    mostrar("Quanto é 3 vezes 4?", conta=True)
    print("=== caso 2: conversa -> assistant -> END (sem tools) ===")
    mostrar("Oi, tudo bem?", conta=False)
    print("=== tool fora da lista vira ToolMessage de erro ===")
    demo_tool_fora_da_lista()
    print("\n=== tool que explode quebra a execução ===")
    demo_erro_na_tool()
    print("\n=== dois pedidos de uma vez ===")
    demo_dois_pedidos()


if __name__ == "__main__":
    main()


# SITUAÇÕES P/ VOCÊ TENTAR:
# 1. Com a chave Groq, pergunte "some 10 com 5" e confira o ToolMessage com "15".
# 2. Pergunte "quanto é 2+2 vezes 3?" e observe quantos tool_calls o LLM emite.
# 3. Adicione `dividir` ao TOOLS e ao cardápio e teste "quanto é 20 dividido por 4?".
