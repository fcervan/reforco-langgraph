"""Aula 2 — Grafo: o básico que tudo o resto usa.

Ideia: estado é um dict compartilhado. Cada nó recebe o estado
e devolve um dict parcial. Por padrão, a chave é SOBRESCRITA.

Grafo: START -> node_1 -> decide_mood -> node_2 | node_3 -> END
Execute: python src/aula02_grafo.py
"""

import random
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    graph_state: str


def node_1(state: State) -> dict:
    return {"graph_state": state["graph_state"] + " Eu estou "}


def node_2(state: State) -> dict:
    return {"graph_state": state["graph_state"] + "cansado!"}


def node_3(state: State) -> dict:
    return {"graph_state": state["graph_state"] + "descansado!"}


def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    # 50/50 como no curso; com seed fica determinístico p/ estudo.
    return "node_2" if random.random() < 0.5 else "node_3"


def build_graph():
    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", decide_mood)
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    return builder.compile()


def main() -> None:
    graph = build_graph()
    for seed in (1, 2):
        random.seed(seed)
        out = graph.invoke({"graph_state": "Oi,"})
        print(f"seed={seed} -> {out['graph_state']}")


if __name__ == "__main__":
    main()


# SITUAÇÃO P/ VOCÊ TENTAR (pedido de lanche):
# Troque graph_state por "pedido", node_1 anexa " + batata",
# decide_mood escolhe node_2 (" + suco") ou node_3 (" + agua").
# Rode 4 vezes e confira os 2 caminhos possíveis.
