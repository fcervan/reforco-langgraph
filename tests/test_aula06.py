import os

import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.aula06_memoria import build_graph


def test_transitorio_esquece_entre_invokes(monkeypatch):
    """Sem checkpointer, o 2o invoke só vê a própria frase (offline: força Fake)."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    graph = build_graph()
    graph.invoke({"messages": [HumanMessage(content="Quanto é 3+4?")]})
    out2 = graph.invoke({"messages": [HumanMessage(content="Dobra isso")]})
    # Uma execução isolada tem 4 msgs (pergunta+pedido+recibo+resposta) e
    # NENHUM vestígio do turno 1 — prova estrutural do esquecimento.
    assert len(out2["messages"]) == 4
    assert all("3+4" not in m.content for m in out2["messages"])


def test_com_memoria_reidrata_turno_anterior(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    graph = build_graph(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}
    graph.invoke({"messages": [HumanMessage(content="Quanto é 3+4?")]}, cfg)
    out2 = graph.invoke({"messages": [HumanMessage(content="Dobra isso")]}, cfg)
    assert len(out2["messages"]) == 8  # turno 1 (4) + turno 2 (4)
    assert out2["messages"][-1].content == "14"


def test_threads_sao_isoladas(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    graph = build_graph(checkpointer=MemorySaver())
    graph.invoke({"messages": [HumanMessage(content="Quanto é 3+4?")]},
                 {"configurable": {"thread_id": "ana"}})
    out_bia = graph.invoke({"messages": [HumanMessage(content="Dobra isso")]},
                           {"configurable": {"thread_id": "bia"}})
    assert len(out_bia["messages"]) == 4  # nada da ana aqui
    assert all("3+4" not in m.content for m in out_bia["messages"])


def test_sem_thread_id_da_valueerror():
    graph = build_graph(checkpointer=MemorySaver())
    with pytest.raises(ValueError):
        graph.invoke({"messages": [HumanMessage(content="oi")]})


def test_historico_cresce_a_cada_passo(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    graph = build_graph(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "hist"}}
    graph.invoke({"messages": [HumanMessage(content="Quanto é 3+4?")]}, cfg)
    graph.invoke({"messages": [HumanMessage(content="Dobra isso")]}, cfg)
    historico = list(graph.get_state_history(cfg))
    assert len(historico) > 2  # um checkpoint por passo do grafo
    atual = graph.get_state(cfg)
    assert len(atual.values["messages"]) == 8


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="só com chave real")
def test_groq_real_lembra_do_7():
    graph = build_graph(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "real"}}
    graph.invoke({"messages": [HumanMessage(content="Quanto é 3 mais 4? Responda só o número.")]}, cfg)
    out2 = graph.invoke(
        {"messages": [HumanMessage(content="Multiplique isso por 2. Responda só o número.")]}, cfg
    )
    assert "14" in out2["messages"][-1].content, out2["messages"][-1].content
