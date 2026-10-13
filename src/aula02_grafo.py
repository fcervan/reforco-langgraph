"""Aula 02 — Grafos: o básico que tudo o resto usa.

Ideia: estado é um dict compartilhado. Cada nó recebe o estado
e devolve um dict PARCIAL. Por padrão, a chave é SOBRESCRITA
(o último nó a escrever ganha).

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
    # 50/50 como no curso. Com random.seed(N) antes do invoke, fica determinístico.
    return "node_2" if random.random() < 0.5 else "node_3"


def build_graph() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", decide_mood)
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    return builder.compile()


def mostrar_trajeto(graph, entrada: str, seed: int | None = None) -> str:
    """Roda o grafo e devolve o caminho percorrido (útil para estudo)."""
    if seed is not None:
        random.seed(seed)
    return graph.invoke({"graph_state": entrada})["graph_state"]


# ---------------------------------------------------------------- demos

def demo_visualizacao(graph) -> None:
    """Mostra como desenhar o grafo: mermaid sempre, ASCII se grandalf existir."""
    print("--- draw_mermaid() (funciona em qualquer ambiente) ---")
    print(graph.get_graph().draw_mermaid())
    print("--- draw_ascii() (precisa de grandalf) ---")
    try:
        print(graph.get_graph().draw_ascii())
    except ImportError as erro:
        print(f"ASCII indisponível ({erro}).")
        print("Para ter: pip install grandalf")


def demo_overwrite() -> None:
    """Dois nós escrevem a MESMA chave em sequencia -> o ultimo ganha (sem erro)."""

    def no_a(state: State) -> dict:
        return {"graph_state": "escrito por A"}

    def no_b(state: State) -> dict:
        return {"graph_state": "escrito por B"}

    builder = StateGraph(State)
    builder.add_node("a", no_a)
    builder.add_node("b", no_b)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("b", END)
    print(builder.compile().invoke({"graph_state": "inicial"}))


def demo_rota_inexistente(graph) -> None:
    """Rota digitada errada NAO quebra: emite aviso e o grafo encerra.

    Armadilha classica: 'node_99' nao existe, o LangGraph avisa
    ('wrote to unknown channel branch:to:node_99, ignoring it') e segue
    para o END. Se voce na ler o aviso, o grafo fica sem a etapa.
    """

    def rota_quebrada(state: State) -> str:
        return "node_99"

    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", rota_quebrada)
    graph_quebrado = builder.compile()
    print(graph_quebrado.invoke({"graph_state": "Oi,"}))
    print("(note que node_2/node_3 NUNCA rodaram — logo nao precisa existir acima)")


def demo_chave_fora_do_schema(graph) -> None:
    """Atualizacao com chave fora do schema e ignorada em silencio (estado intacto)."""

    def chave_inventada(state: State) -> dict:
        return {"nao_existe": 123}

    builder = StateGraph(State)
    builder.add_node("inventor", chave_inventada)
    builder.add_edge(START, "inventor")
    builder.add_edge("inventor", END)
    print(builder.compile().invoke({"graph_state": "valor original"}))


def main() -> None:
    graph = build_graph()

    print("=== trajetos deterministicos (seed) ===")
    for seed in (1, 2, 3, 4):
        print(f"seed={seed} -> {mostrar_trajeto(graph, 'Oi,', seed)}")

    print("\n=== overwrite (dois nos, mesma chave) ===")
    demo_overwrite()

    print("\n=== rota inexistente (aviso silencioso) ===")
    demo_rota_inexistente(graph)

    print("\n=== chave fora do schema (ignorada) ===")
    demo_chave_fora_do_schema(graph)

    print("\n=== visualizacao ===")
    demo_visualizacao(graph)


if __name__ == "__main__":
    main()
