"""Aula 15 — Viagem no tempo: reproduzir o passado e criar futuros alternativos.

Cada passo do grafo grava um checkpoint. Com eles você:
- NAVEGA: get_state_history(cfg) lista do mais novo ao mais antigo;
- REPRODUZ: stream(None, config_antiga) reexecuta a partir dali;
- BIFURCA (fork): update_state(config_antiga, {...}) cria um ramo novo —
  o passado original continua intacto.

Sem LLM nesta aula (100% offline, Fake determinístico).
Execute: python src/aula15_tempo.py
"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


def multiply(a: int, b: int) -> int:
    """Multiplica a por b."""
    return a * b


def fake_pedido():
    """Fake com pedido + frase final. CRIADO UMA VEZ por grafo."""
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                id="pedido-1",
                tool_calls=[
                    {"name": "multiply", "args": {"a": 2, "b": 3}, "id": "c1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="6", id="resp-1", tool_calls=[]),
        ]
    )


def build_graph():
    llm = fake_pedido()

    def assistant(state: MessagesState) -> dict:
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode([multiply]))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=MemorySaver())


def demo_navega() -> list:
    """Roda uma vez e lista os checkpoints (do mais novo ao mais antigo)."""
    graph = build_graph()
    cfg = {"configurable": {"thread_id": "viagem"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 2 e 3", id="hum-1")]}, cfg))
    historico = list(graph.get_state_history(cfg))
    print(f"{len(historico)} checkpoints (mais novo primeiro):")
    for h in historico:
        cid = h.config["configurable"]["checkpoint_id"][:8]
        print(f"   id={cid} next={h.next} msgs={len(h.values['messages'])}")
    return graph, cfg, historico


def demo_reproduz(graph, historico) -> None:
    """stream(None, config_antiga): reproduz a partir daquele ponto."""
    antigo = historico[-2]  # o checkpoint que recebeu a pergunta humana
    print("reproduzindo a partir do checkpoint da pergunta:")
    for chunk in graph.stream(None, antigo.config, stream_mode="updates"):
        print("   ", list(chunk.keys()))
    print("-> mesmos nós, sem reescrever o passado.")


def demo_bifurca(graph, cfg, historico):
    """update_state(config_antiga, ...): novo ramo; passado intacto."""
    antigo = historico[-2]
    fork_cfg = graph.update_state(
        antigo.config,
        {"messages": [HumanMessage(content="Some 5 e 3", id="hum-1")]},
    )
    print("novo checkpoint (fork) criado.")
    for chunk in graph.stream(None, fork_cfg, stream_mode="updates"):
        print("   ", list(chunk.keys()))
    atual = [(type(m).__name__, m.content) for m in graph.get_state(cfg).values["messages"]]
    print("estado atual do ramo novo:", atual)
    return fork_cfg


def main() -> None:
    print("=== 1. navega o histórico ===")
    graph, cfg, historico = demo_navega()
    print("\n=== 2. reproduz o passado ===")
    demo_reproduz(graph, historico)
    print("\n=== 3. bifurca: troca a pergunta no passado ===")
    demo_bifurca(graph, cfg, historico)


if __name__ == "__main__":
    main()
