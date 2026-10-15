"""Aula 13 — Feedback humano: o fiscal que risca e reescreve o pedido.

Na Aula 12 o humano só carimbava (retomava ou não). Aqui ele EDITA:
- `update_state(cfg, {...})` sem `id` -> ANEXA (novo contexto);
- com o MESMO `id` -> SOBRESCREVE (corrige o pedido pendente);
- `as_node="feedback_humano"` -> assina a edição com nome de nó (exige que
  o nó placeholder exista no grafo, senão InvalidUpdateError).

Execute: python src/aula13_feedback.py
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


def fake_pedido_soma():
    """Fake: pede add(3,4) e depois encerra. CRIADO UMA VEZ por grafo."""
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                id="pedido-1",
                tool_calls=[
                    {"name": "add", "args": {"a": 3, "b": 4}, "id": "c1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="Fechado.", tool_calls=[]),
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
    return fake_pedido_soma()


def make_assistant(llm=None):
    llm = llm or get_llm()

    def assistant(state: MessagesState) -> dict:
        return {"messages": [llm.invoke([SystemMessage(content=SISTEMA)] + state["messages"])]}

    return assistant


def build_base(llm=None, com_feedback: bool = False):
    """ReAct com pausa antes das tools; com_feedback=True adiciona o nó placeholder."""
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    if com_feedback:
        builder.add_node("feedback_humano", lambda state: {})
        builder.add_edge(START, "feedback_humano")
        builder.add_edge("feedback_humano", "assistant")
    else:
        builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=MemorySaver(), interrupt_before=["tools"])


def pausa(cfg_thread: str = "demo", llm=None, com_feedback: bool = False):
    graph = build_base(llm=llm, com_feedback=com_feedback)
    cfg = {"configurable": {"thread_id": cfg_thread}}
    list(
        graph.stream(
            {"messages": [HumanMessage(content="Some 3 e 4")]}, cfg, stream_mode="updates"
        )
    )
    return graph, cfg


def demo_corrige_pedido() -> None:
    """MESMO id: troca add(3,4) por multiply(3,10) antes de executar."""
    graph, cfg = pausa("corrige", llm=fake_pedido_soma())
    pedido = graph.get_state(cfg).values["messages"][-1]
    print(f"pedido parado: {pedido.tool_calls[0]['name']}{pedido.tool_calls[0]['args']}")
    corrigido = AIMessage(
        content="",
        id=pedido.id,  # MESMO id -> sobrescreve, não anexa
        tool_calls=[
            {"name": "multiply", "args": {"a": 3, "b": 10}, "id": "c1", "type": "tool_call"}
        ],
    )
    graph.update_state(cfg, {"messages": [corrigido]})
    list(graph.stream(None, cfg))
    final = graph.get_state(cfg).values["messages"]
    print("recibos:", [(type(m).__name__, m.content) for m in final if type(m).__name__ == "ToolMessage"])
    print("-> o '30' prova que executou o pedido CORRIGIDO, não o original.")


def demo_anexa_contexto() -> None:
    """SEM id: anexa contexto novo (o pedido original continua valendo)."""
    graph, cfg = pausa("anexa", llm=fake_pedido_soma())
    graph.update_state(cfg, {"messages": [HumanMessage(content="urgente: preciso hoje")]})
    msgs = graph.get_state(cfg).values["messages"]
    print(f"mensagens após anexar: {len(msgs)} (era 2: pergunta + pedido)")
    print("-> anexar soma; só o MESMO id substitui.")


def demo_feedback_assinado() -> None:
    """Placeholder + as_node: a edição entra assinada como 'feedback_humano'."""
    builder = StateGraph(MessagesState)
    llm = fake_pedido_soma()
    builder.add_node("assistant", make_assistant(llm))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("feedback_humano", lambda state: {})
    builder.add_edge(START, "feedback_humano")
    builder.add_edge("feedback_humano", "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    graph = builder.compile(checkpointer=MemorySaver(), interrupt_before=["feedback_humano"])
    cfg = {"configurable": {"thread_id": "assinado"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    print("pausado em:", graph.get_state(cfg).next)
    graph.update_state(
        cfg,
        {"messages": [HumanMessage(content="na verdade quero o dobro: some 7 e 7")]},
        as_node="feedback_humano",
    )
    list(graph.stream(None, cfg))
    msgs = graph.get_state(cfg).values["messages"]
    print("histórico:", [(type(m).__name__, m.content) for m in msgs])


def demo_as_node_inexistente() -> None:
    """as_node exige nó existente: nome inventado morre com InvalidUpdateError."""
    graph, cfg = pausa("fantasma", llm=fake_pedido_soma())
    try:
        graph.update_state(cfg, {"messages": [HumanMessage(content="oi")]}, as_node="fantasma")
    except Exception as erro:
        print(f"{type(erro).__name__}: {str(erro)[:60]}")
        print("-> por isso existe o nó placeholder: ele dá nome ao humano no histórico.")


def main() -> None:
    print("=== 1. corrige o pedido (mesmo id) ===")
    demo_corrige_pedido()
    print("\n=== 2. anexa contexto (sem id) ===")
    demo_anexa_contexto()
    print("\n=== 3. feedback assinado (placeholder + as_node) ===")
    demo_feedback_assinado()
    print("\n=== 4. as_node inexistente ===")
    demo_as_node_inexistente()


if __name__ == "__main__":
    main()
