"""Aula 05 — Agente ReAct: o loop pensar -> agir -> observar.

A única novidade em relação à Aula 04 é UMA aresta: `tools -> assistant`.
Com ela, o LLM relê o recibo (`ToolMessage`), pode pedir MAIS tools e só
encerra quando responde sem `tool_calls`. É o loop que move atendimentos
reais (pastel -> valor? -> +refri -> cancela -> conta).

Execute: python src/aula05_agente.py
Com GROQ_API_KEY usa Groq real (gpt-oss-20b); sem chave roda offline (Fake).
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

MODELO = "openai/gpt-oss-20b"
SISTEMA = "Você é um assistente que faz contas. Responda em português."
TOOLS = []


def add(a: int, b: int) -> int:
    """Soma a e b."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiplica a por b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a por b."""
    return a / b


TOOLS = [add, multiply, divide]


def get_llm():
    """Groq com cardápio [add, multiply, divide] — ou Fake offline."""
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print("AVISO: langchain_groq ausente -> seguirei no Fake offline.")
        else:
            # reasoning_effort="low": sem tool_calls o loop nem começa (Aula 01).
            return ChatGroq(
                model=MODELO, temperature=0, reasoning_effort="low"
            ).bind_tools(TOOLS)
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 3, "b": 4}, "id": "c1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="O resultado é 7.", tool_calls=[]),
        ]
    )


def make_assistant(llm=None):
    llm = llm or get_llm()

    def assistant(state: MessagesState) -> dict:
        # SYS vai só na chamada (não é gravado no estado).
        return {"messages": [llm.invoke([SystemMessage(content=SISTEMA)] + state["messages"])]}

    return assistant


def build_graph(llm=None, loop_back: bool = True):
    """loop_back=True: ReAct (tools -> assistant). False: Aula 04 (tools -> END)."""
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant" if loop_back else END)
    return builder.compile()


def mostrar_trajeto(graph, pergunta: str, **invoke_kwargs) -> list:
    out = graph.invoke({"messages": [HumanMessage(content=pergunta)]}, **invoke_kwargs)
    for m in out["messages"]:
        print(f"   [{type(m).__name__}] {str(m.content)!r} {getattr(m, 'tool_calls', '')}")
    return out["messages"]


def demo_sem_volta() -> None:
    """Contraste com a Aula 04: sem a volta, o LLM nunca vê o recibo."""
    print("SEM volta (Aula 04: tools -> END, o '7' morre no recibo):")
    mostrar_trajeto(build_graph(loop_back=False), "Some 3 e 4")


def demo_limite_recursao() -> None:
    """Trava de segurança: loop sem fim morre com GraphRecursionError."""
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    teimoso = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 1, "b": 1}, "id": "c9", "type": "tool_call"}
                ],
            )
        ]
    )
    graph = build_graph(llm=teimoso, loop_back=True)
    try:
        graph.invoke(
            {"messages": [HumanMessage(content="Some 1 e 1")]},
            config={"recursion_limit": 3},
        )
    except GraphRecursionError as erro:
        print(f"   GraphRecursionError (limite 3): {str(erro)[:80]}...")
        print("   -> todo agente precisa de limite; o padrão é 25 passos.")


def main() -> None:
    if os.getenv("GROQ_API_KEY"):
        print("=== ReAct real: 3 contas encadeadas ===")
        mostrar_trajeto(
            build_graph(loop_back=True),
            "Some 3 e 4, depois multiplique por 2, e finalmente divida por 5. Mostre o resultado.",
        )
    else:
        print("=== ReAct offline (Fake): pedido -> recibo -> resposta final ===")
        mostrar_trajeto(build_graph(loop_back=True), "Some 3 e 4")
    print()
    demo_sem_volta()
    print()
    print("=== limite de recursão (trava de segurança) ===")
    demo_limite_recursao()


if __name__ == "__main__":
    main()
