from langchain_core.messages import HumanMessage

from src.aula15_tempo import build_graph


def _roda(thread: str = "t"):
    graph = build_graph()
    cfg = {"configurable": {"thread_id": thread}}
    list(graph.stream({"messages": [HumanMessage(content="Multiplique 2 e 3", id="hum-1")]}, cfg))
    return graph, cfg


def test_historico_do_novo_ao_antigo():
    graph, cfg = _roda("h1")
    historico = list(graph.get_state_history(cfg))
    assert len(historico) == 5  # input + 3 passos + final
    assert historico[0].next == ()  # mais novo: parado no END
    assert historico[-1].next == ("__start__",)  # mais antigo: antes de tudo
    for h in historico:
        assert "checkpoint_id" in h.config["configurable"]


def test_reproduz_mesmos_nos():
    graph, cfg = _roda("h2")
    historico = list(graph.get_state_history(cfg))
    antigo = historico[-2]
    chunks = list(graph.stream(None, antigo.config, stream_mode="updates"))
    assert [list(c.keys()) for c in chunks] == [["assistant"], ["tools"], ["assistant"]]


def test_fork_troca_pergunta_mantem_id():
    graph, cfg = _roda("h3")
    historico = list(graph.get_state_history(cfg))
    graph.update_state(
        historico[-2].config,
        {"messages": [HumanMessage(content="Multiplique 5 e 3", id="hum-1")]},
    )
    atual = graph.get_state(cfg).values["messages"]
    assert atual[0].content == "Multiplique 5 e 3"
    assert atual[0].id == "hum-1"  # mesmo id: substituiu, não anexou


def test_fork_executa_ramo_novo():
    graph, cfg = _roda("h4")
    historico = list(graph.get_state_history(cfg))
    fork_cfg = graph.update_state(
        historico[-2].config,
        {"messages": [HumanMessage(content="Multiplique 5 e 3", id="hum-1")]},
    )
    chunks = list(graph.stream(None, fork_cfg, stream_mode="updates"))
    assert [list(c.keys()) for c in chunks] == [["assistant"], ["tools"], ["assistant"]]
    final = graph.get_state(cfg).values["messages"][-1]
    assert type(final).__name__ == "AIMessage"
