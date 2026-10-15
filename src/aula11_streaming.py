"""Aula 11 — Streaming: ver o grafo executando (base do humano-no-loop).

`invoke` devolve só o estado FINAL. `stream` devolve um GERADOR que emite
a execução aos poucos, em 3 modos:
- updates: o DELTA de cada nó ({'assistant': {...}}, {'tools': {...}}).
- values: o estado COMPLETO após cada nó (1, 2, 3, 4 msgs...).
- messages: tuplas (pedacinho, metadata) com `langgraph_node` de origem.

Execute: python src/aula11_streaming.py
Com GROQ_API_KEY mostra tokens reais; sem chave roda offline (Fake).
"""

import asyncio
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
    """Fake com 2 falas: pedido de tool, depois frase final. CRIADO UMA VEZ
    fora do nó: criar dentro faria cada volta ganhar um Fake 'zerado' e o
    loop nunca terminaria (mesma regra da Aula 06)."""
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


def build_graph(llm=None, checkpointer=None):
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=checkpointer)


def demo_updates() -> None:
    print("updates (delta por nó):")
    graph = build_graph(checkpointer=MemorySaver())
    for chunk in graph.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]},
        {"configurable": {"thread_id": "u1"}},
        stream_mode="updates",
    ):
        print("  ", list(chunk.keys()), "->", str(chunk)[:110].replace("\n", " "))


def demo_values() -> None:
    print("values (estado completo após cada nó):")
    graph = build_graph(checkpointer=MemorySaver())
    for chunk in graph.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]},
        {"configurable": {"thread_id": "u2"}},
        stream_mode="values",
    ):
        print(f"   estado com {len(chunk['messages'])} msgs")


def demo_messages() -> None:
    print("messages (tupla chunk + metadata):")
    graph = build_graph(checkpointer=MemorySaver())
    for pedaco, meta in graph.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]},
        {"configurable": {"thread_id": "u3"}},
        stream_mode="messages",
    ):
        print(f"   [{type(pedaco).__name__} do nó {meta.get('langgraph_node')}] {pedaco.content!r}")


def demo_tokens_reais() -> None:
    """Com Groq real: os pedacinhos da resposta final, ao vivo."""
    if not os.getenv("GROQ_API_KEY"):
        print("(sem chave: tokens reais só com Groq; o modo messages acima mostra a estrutura.)")
        return
    print("tokens reais (Groq, nó assistant):")
    graph = build_graph(checkpointer=MemorySaver())

    async def ver():
        async for ev in graph.astream_events(
            {"messages": [HumanMessage(content="Some 3 e 4. Responda com frase.")]},
            {"configurable": {"thread_id": "u4"}},
            version="v2",
        ):
            if ev["event"] == "on_chat_model_stream" and ev["metadata"].get("langgraph_node") == "assistant":
                print(ev["data"]["chunk"].content, end="", flush=True)
        print()

    asyncio.run(ver())


def main() -> None:
    print("=== 1. updates ===")
    demo_updates()
    print("\n=== 2. values ===")
    demo_values()
    print("\n=== 3. messages ===")
    demo_messages()
    print("\n=== 4. tokens reais ===")
    demo_tokens_reais()


if __name__ == "__main__":
    main()
