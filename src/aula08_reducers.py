"""Aula 08 — Reducers: a regra de mesclagem do estado.

Por padrão, cada chave aceita UM valor por etapa (overwrite). Quando dois nós
escrevem na mesma etapa (fan-out paralelo), o LangGraph exige uma regra de
mesclagem — o *reducer* — ou aborta com InvalidUpdateError.

Sem LLM nesta aula (100% offline). Execute: python src/aula08_reducers.py
"""

from operator import add
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages


class EstadoOverwrite(TypedDict):
    foo: int


class EstadoLista(TypedDict):
    foo: Annotated[list, add]


def reduce_seguro(esquerda: list | None, direita: list | None) -> list:
    """Reducer customizado tolerante a None (operator.add quebra com None)."""
    if esquerda is None:
        return direita or []
    if direita is None:
        return esquerda
    return esquerda + direita


class EstadoCustom(TypedDict):
    foo: Annotated[list, reduce_seguro]


class EstadoEstendido(MessagesState):
    resumo: str  # canal extra convive com messages


def demo_sequencial_ok() -> None:
    """Em sequência, overwrite funciona: último nó ganha, sem erro."""
    builder = StateGraph(EstadoOverwrite)
    builder.add_node("n1", lambda s: {"foo": s["foo"] + 1})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", END)
    print("sequencial:", builder.compile().invoke({"foo": 1}))


def demo_fanout_quebra() -> None:
    """Fan-out sem reducer: dois valores na mesma etapa -> InvalidUpdateError."""
    builder = StateGraph(EstadoOverwrite)
    builder.add_node("n1", lambda s: {"foo": s["foo"] + 1})
    builder.add_node("n2", lambda s: {"foo": s["foo"] + 1})
    builder.add_node("n3", lambda s: {"foo": s["foo"] + 1})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n1", "n3")
    builder.add_edge("n2", END)
    builder.add_edge("n3", END)
    try:
        builder.compile().invoke({"foo": 1})
    except InvalidUpdateError as erro:
        print("fan-out sem reducer -> InvalidUpdateError:")
        print("  ", str(erro).split("\n")[0])


def demo_operator_add() -> None:
    """Com operator.add, os paralelos SOMAM: [1] -> n1 faz [1,2] -> n2/n3
    leem [1,2] e anexam 3 cada um -> [1, 2, 3, 3]."""
    builder = StateGraph(EstadoLista)
    builder.add_node("n1", lambda s: {"foo": [s["foo"][-1] + 1]})
    builder.add_node("n2", lambda s: {"foo": [s["foo"][-1] + 1]})
    builder.add_node("n3", lambda s: {"foo": [s["foo"][-1] + 1]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n1", "n3")
    builder.add_edge("n2", END)
    builder.add_edge("n3", END)
    print("fan-out com add:", builder.compile().invoke({"foo": [1]}))


def demo_none_quebra_e_custom_salva() -> None:
    """operator.add com None -> TypeError; reducer custom tolera."""
    builder = StateGraph(EstadoLista)
    builder.add_node("n1", lambda s: {"foo": [2]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", END)
    try:
        builder.compile().invoke({"foo": None})
    except TypeError as erro:
        print(f"add + None -> TypeError: {erro}")

    builder2 = StateGraph(EstadoCustom)
    builder2.add_node("n1", lambda s: {"foo": [2]})
    builder2.add_edge(START, "n1")
    builder2.add_edge("n1", END)
    print("custom + None:", builder2.compile().invoke({"foo": None}))


def demo_poderes_do_add_messages() -> None:
    """Os 3 poderes do add_messages: anexar, sobrescrever por id, remover."""
    print("anexar:", [m.content for m in add_messages(
        [HumanMessage(content="oi")], [AIMessage(content="olá")])])
    print("sobrescrever id:", [m.content for m in add_messages(
        [AIMessage(content="velha", id="1")],
        [HumanMessage(content="nova mesma id", id="1")])])
    print("remover:", [m.content for m in add_messages(
        [AIMessage(content="a", id="1"), HumanMessage(content="b", id="2"),
         AIMessage(content="c", id="3")],
        [RemoveMessage(id="1"), RemoveMessage(id="2")])])


def demo_estendido() -> None:
    """MessagesState com canal extra: messages tem reducer, resumo sobrescreve."""
    builder = StateGraph(EstadoEstendido)
    builder.add_node("n", lambda s: {"resumo": "r", "messages": [AIMessage(content="oi")]})
    builder.add_edge(START, "n")
    builder.add_edge("n", END)
    out = builder.compile().invoke({"messages": [], "resumo": ""})
    print("estendido:", out["resumo"], "|", [m.content for m in out["messages"]])


def main() -> None:
    print("=== 1. sequência: overwrite ok ===")
    demo_sequencial_ok()
    print("\n=== 2. fan-out sem reducer: quebra ===")
    demo_fanout_quebra()
    print("\n=== 3. fan-out com operator.add ===")
    demo_operator_add()
    print("\n=== 4. None: add quebra, custom salva ===")
    demo_none_quebra_e_custom_salva()
    print("\n=== 5. os 3 poderes do add_messages ===")
    demo_poderes_do_add_messages()
    print("\n=== 6. MessagesState estendido ===")
    demo_estendido()


if __name__ == "__main__":
    main()
