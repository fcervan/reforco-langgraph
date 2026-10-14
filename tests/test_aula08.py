import pytest
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages

from src.aula08_reducers import (
    EstadoCustom,
    EstadoEstendido,
    EstadoLista,
    EstadoOverwrite,
    reduce_seguro,
)


def fanout(schema, fn):
    builder = StateGraph(schema)
    builder.add_node("n1", fn)
    builder.add_node("n2", fn)
    builder.add_node("n3", fn)
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n1", "n3")
    builder.add_edge("n2", END)
    builder.add_edge("n3", END)
    return builder.compile()


def test_sequencial_overwrite_ultimo_ganha():
    builder = StateGraph(EstadoOverwrite)
    builder.add_node("n1", lambda s: {"foo": s["foo"] + 1})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", END)
    assert builder.compile().invoke({"foo": 1}) == {"foo": 2}


def test_fanout_sem_reducer_quebra():
    with pytest.raises(InvalidUpdateError):
        fanout(EstadoOverwrite, lambda s: {"foo": s["foo"] + 1}).invoke({"foo": 1})


def test_fanout_com_add_acumula():
    out = fanout(EstadoLista, lambda s: {"foo": [s["foo"][-1] + 1]}).invoke({"foo": [1]})
    # n1: [1,2]; n2/n3 leem [1,2] e anexam 3 cada um
    assert out == {"foo": [1, 2, 3, 3]}


def test_add_com_none_quebra():
    builder = StateGraph(EstadoLista)
    builder.add_node("n1", lambda s: {"foo": [2]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", END)
    with pytest.raises(TypeError):
        builder.compile().invoke({"foo": None})


def test_custom_tolera_none():
    assert reduce_seguro(None, [2]) == [2]
    assert reduce_seguro([1], None) == [1]
    assert reduce_seguro(None, None) == []
    assert reduce_seguro([1], [2]) == [1, 2]
    builder = StateGraph(EstadoCustom)
    builder.add_node("n1", lambda s: {"foo": [2]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", END)
    assert builder.compile().invoke({"foo": None}) == {"foo": [2]}


def test_add_messages_anexa():
    out = add_messages([HumanMessage(content="oi")], [AIMessage(content="olá")])
    assert [m.content for m in out] == ["oi", "olá"]


def test_add_messages_sobrescreve_por_id():
    out = add_messages(
        [AIMessage(content="velha", id="1")],
        [HumanMessage(content="nova", id="1")],
    )
    assert [m.content for m in out] == ["nova"]


def test_add_messages_remove():
    out = add_messages(
        [AIMessage(content="a", id="1"), HumanMessage(content="b", id="2")],
        [RemoveMessage(id="1"), RemoveMessage(id="2")],
    )
    assert [m.content for m in out] == []


def test_estado_estendido():
    builder = StateGraph(EstadoEstendido)
    builder.add_node(
        "n", lambda s: {"resumo": "r", "messages": [AIMessage(content="oi")]}
    )
    builder.add_edge(START, "n")
    builder.add_edge("n", END)
    out = builder.compile().invoke({"messages": [], "resumo": ""})
    assert out["resumo"] == "r"
    assert [m.content for m in out["messages"]] == ["oi"]


def test_contador_paralelo_soma():
    """Desafio: cozinha +1 e bar +1 partindo de 0 somam 2."""
    from operator import add
    from typing import Annotated, TypedDict

    class Contador(TypedDict):
        foo: Annotated[int, add]

    builder = StateGraph(Contador)
    builder.add_node("cozinha", lambda s: {"foo": 1})
    builder.add_node("bar", lambda s: {"foo": 1})
    builder.add_edge(START, "cozinha")
    builder.add_edge(START, "bar")
    builder.add_edge("cozinha", END)
    builder.add_edge("bar", END)
    assert builder.compile().invoke({"foo": 0}) == {"foo": 2}
