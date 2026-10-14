"""Aula 06 — Memória: o agente que lembra entre mensagens.

Sem checkpointer, cada `invoke` é um mundo novo (como HTTP sem cookie):
"Multiplique isso por 2" não sabe o que é "isso".
Com `compile(checkpointer=MemorySaver())` + `thread_id`, cada turno reidrata
o estado salvo — e "isso=7" vira 14.

Execute: python src/aula06_memoria.py
Com GROQ_API_KEY usa Groq real (gpt-oss-20b); sem chave roda offline (Fake).
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


def get_llm():
    """Groq com cardápio — ou Fake offline (sequência de 2 turnos)."""
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            print("AVISO: langchain_groq ausente -> seguirei no Fake offline.")
        else:
            return ChatGroq(
                model=MODELO, temperature=0, reasoning_effort="low"
            ).bind_tools(TOOLS)
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    # Turno 1: pede soma(3,4), encerra com "7". Turno 2: soma(7,7), encerra com "14".
    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 3, "b": 4}, "id": "c1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="7", tool_calls=[]),
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 7, "b": 7}, "id": "c2", "type": "tool_call"}
                ],
            ),
            AIMessage(content="14", tool_calls=[]),
        ]
    )


def make_assistant(llm=None):
    llm = llm or get_llm()

    def assistant(state: MessagesState) -> dict:
        return {"messages": [llm.invoke([SystemMessage(content=SISTEMA)] + state["messages"])]}

    return assistant


def build_graph(llm=None, checkpointer=None):
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=checkpointer)


def turno(graph, frase: str, config: dict | None = None) -> list:
    out = graph.invoke({"messages": [HumanMessage(content=frase)]}, config)
    msgs = out["messages"]
    print(f"   P: {frase}")
    print(f"   R: {msgs[-1].content!r} (estado agora tem {len(msgs)} msgs)")
    return msgs


def demo_transitorio() -> None:
    """SEM checkpointer: o turno 2 não vê o turno 1 (só a própria frase)."""
    print("SEM checkpointer (cada invoke é um mundo novo):")
    graph = build_graph()
    turno(graph, "Quanto é 3 mais 4? Responda só o número.")
    msgs = turno(graph, "Multiplique isso por 2. Responda só o número.")
    print(f"   -> turno 2 viu {len(msgs)} mensagem(ns): esqueceu o 7.")


def demo_com_memoria() -> None:
    """COM checkpointer + mesma thread: o turno 2 reidrata o turno 1."""
    print("COM checkpointer (thread única, 'isso' = 7):")
    graph = build_graph(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "sessao-1"}}
    turno(graph, "Quanto é 3 mais 4? Responda só o número.", cfg)
    msgs = turno(graph, "Multiplique isso por 2. Responda só o número.", cfg)
    print(f"   -> turno 2 viu {len(msgs)} mensagens: lembrou do 7.")


def demo_isolamento() -> None:
    """Thread diferente = conversa diferente (sem vazamento)."""
    print("ISOLAMENTO (outra thread não vê a sessão 1):")
    graph = build_graph(checkpointer=MemorySaver())
    cfg1 = {"configurable": {"thread_id": "ana"}}
    turno(graph, "Quanto é 3 mais 4? Responda só o número.", cfg1)
    cfg2 = {"configurable": {"thread_id": "bia"}}
    msgs = turno(graph, "Multiplique isso por 2. Responda só o número.", cfg2)
    print(f"   -> 'bia' viu {len(msgs)} mensagem(ns): nada da 'ana'.")


def demo_sem_thread_id() -> None:
    """Grafo COM checkpointer exige thread_id: sem ele, ValueError."""
    print("SEM thread_id (erro de construção do uso):")
    graph = build_graph(checkpointer=MemorySaver())
    try:
        graph.invoke({"messages": [HumanMessage(content="oi")]})
    except ValueError as erro:
        print(f"   ValueError: {str(erro)[:100]}...")


def main() -> None:
    demo_transitorio()
    print()
    demo_com_memoria()
    print()
    demo_isolamento()
    print()
    demo_sem_thread_id()


if __name__ == "__main__":
    main()
