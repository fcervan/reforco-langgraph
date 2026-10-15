"""Aula 12 — Breakpoints: pausar para aprovação humana e retomar.

`interrupt_before=["tools"]` pausa o grafo ANTES de executar a tool:
- o `stream` emite `__interrupt__` e para;
- `get_state(cfg).next` diz onde parou (`('tools',)`);
- `stream(None, cfg)` retoma de onde parou (exige checkpointer!).

Execute: python src/aula12_breakpoints.py
Com GROQ_API_KEY usa Groq real; sem chave roda offline (Fake).
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

MODELO = "openai/gpt-oss-20b"
SISTEMA = "Você é um assistente que faz contas. Responda em português, de forma curta."
TOOLS = []


def add(a: int, b: int) -> int:
    """Soma a e b."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiplica a por b."""
    return a * b


TOOLS = [add, multiply]


def fake_duas_falas():
    """Fake com 2 falas. CRIADO UMA VEZ fora do nó (regra das Aulas 06/11)."""
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


def get_llm():
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print("AVISO: langchain_groq ausente -> seguirei no Fake offline.")
        else:
            return ChatGroq(
                model=MODELO, temperature=0, reasoning_effort="low"
            ).bind_tools(TOOLS)
    print("AVISO: modo Fake offline.")
    return fake_duas_falas()


def make_assistant(llm=None):
    llm = llm or get_llm()

    def assistant(state: MessagesState) -> dict:
        return {"messages": [llm.invoke([SystemMessage(content=SISTEMA)] + state["messages"])]}

    return assistant


def build_graph(llm=None, checkpointer=None, interrupt_before=("tools",)):
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=checkpointer, interrupt_before=list(interrupt_before))


def demo_pausa_inspeciona_retoma(llm=None) -> None:
    """Ciclo completo: pausa -> inspeciona -> retoma."""
    graph = build_graph(llm=llm, checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "pausa-1"}}
    print("1) stream até pausar:")
    for chunk in graph.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]}, cfg, stream_mode="updates"
    ):
        print("   ", list(chunk.keys()))
    estado = graph.get_state(cfg)
    print("2) inspeciona: next =", estado.next)
    pedido = estado.values["messages"][-1].tool_calls[0]
    print(f"   tool pendente: {pedido['name']}{pedido['args']} (id={pedido['id']})")
    print("3) retoma com stream(None):")
    for chunk in graph.stream(None, cfg, stream_mode="updates"):
        print("   ", list(chunk.keys()))
    final = graph.get_state(cfg)
    print("4) fim: next =", final.next, "| resposta:", repr(final.values["messages"][-1].content))


def demo_sem_checkpointer_nao_retoma() -> None:
    """Compila com interrupt, pausa — mas retomar com None morre sem sessão."""
    graph = build_graph(llm=fake_duas_falas())
    print("pausa (funciona até sem checkpointer):")
    for chunk in graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}):
        print("   ", list(chunk.keys()))
    print("retoma com None (sem sessão salva):")
    try:
        for chunk in graph.stream(None):
            print("   ", list(chunk.keys()))
    except Exception as erro:
        print(f"   {type(erro).__name__}: {str(erro)[:80]}")
        print("   -> retomar entre chamadas EXIGE checkpointer (a pausa não).")


def demo_interrupt_after() -> None:
    """interrupt_after=['assistant']: pausa DEPOIS do nó (mesmo next)."""
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm=fake_duas_falas()))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    graph2 = builder.compile(checkpointer=MemorySaver(), interrupt_after=["assistant"])
    cfg = {"configurable": {"thread_id": "after-1"}}
    for chunk in graph2.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]}, cfg, stream_mode="updates"
    ):
        print("   ", list(chunk.keys()))
    print("   next:", graph2.get_state(cfg).next)
    print("   (before pausa ANTES do nó; after pausa DEPOIS — aqui dá no mesmo ponto)")


def main() -> None:
    print("=== 1. pausa -> inspeciona -> retoma ===")
    demo_pausa_inspeciona_retoma()
    print("\n=== 2. sem checkpointer não retoma ===")
    demo_sem_checkpointer_nao_retoma()
    print("\n=== 3. interrupt_after ===")
    demo_interrupt_after()


if __name__ == "__main__":
    main()
