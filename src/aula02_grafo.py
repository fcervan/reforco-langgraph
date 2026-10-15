"""Aula 02 — Grafos: o básico que tudo o resto usa.

Ideia: estado é um dict compartilhado. Cada nó recebe o estado
e devolve um dict PARCIAL. Por padrão, a chave é SOBRESCRITA
(o último nó a escrever ganha).

Grafo: START -> no_recebe -> decide_bebida -> no_suco | no_agua -> END

Execute: python src/aula02_grafo.py
"""

import random
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    pedido: str


def no_recebe(state: State) -> dict:
    return {"pedido": state["pedido"] + "hamburguer"}


def no_suco(state: State) -> dict:
    return {"pedido": state["pedido"] + " + suco"}


def no_agua(state: State) -> dict:
    return {"pedido": state["pedido"] + " + água"}


def decide_bebida(state: State) -> Literal["no_suco", "no_agua"]:
    # 50/50. Com random.seed(N) antes do invoke, fica determinístico.
    return "no_suco" if random.random() < 0.5 else "no_agua"


def build_graph() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("no_recebe", no_recebe)
    builder.add_node("no_suco", no_suco)
    builder.add_node("no_agua", no_agua)
    builder.add_edge(START, "no_recebe")
    builder.add_conditional_edges("no_recebe", decide_bebida)
    builder.add_edge("no_suco", END)
    builder.add_edge("no_agua", END)
    return builder.compile()


def mostrar_trajeto(graph, entrada: str, seed: int | None = None) -> str:
    """Roda o grafo e devolve o caminho percorrido (útil para estudo)."""
    if seed is not None:
        random.seed(seed)
    return graph.invoke({"pedido": entrada})["pedido"]


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
        return {"pedido": "escrito por A"}

    def no_b(state: State) -> dict:
        return {"pedido": "escrito por B"}

    builder = StateGraph(State)
    builder.add_node("a", no_a)
    builder.add_node("b", no_b)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("b", END)
    print(builder.compile().invoke({"pedido": "inicial"}))


def demo_rota_inexistente(graph) -> None:
    """Rota digitada errada NAO quebra: emite aviso e o grafo encerra.

    Armadilha classica: 'bebida_99' nao existe, o LangGraph avisa
    ('wrote to unknown channel branch:to:bebida_99, ignoring it') e segue
    para o END. Se voce na ler o aviso, o grafo fica sem a etapa.
    """

    def rota_quebrada(state: State) -> str:
        return "bebida_99"

    builder = StateGraph(State)
    builder.add_node("no_recebe", no_recebe)
    builder.add_edge(START, "no_recebe")
    builder.add_conditional_edges("no_recebe", rota_quebrada)
    graph_quebrado = builder.compile()
    print(graph_quebrado.invoke({"pedido": "Pedido: "}))
    print("(note que no_suco/no_agua NUNCA rodaram — logo nao precisa existir acima)")


def demo_chave_fora_do_schema(graph) -> None:
    """Atualizacao com chave fora do schema e ignorada em silencio (estado intacto)."""

    def chave_inventada(state: State) -> dict:
        return {"nao_existe": 123}

    builder = StateGraph(State)
    builder.add_node("inventor", chave_inventada)
    builder.add_edge(START, "inventor")
    builder.add_edge("inventor", END)
    print(builder.compile().invoke({"pedido": "valor original"}))


def main() -> None:
    graph = build_graph()

    print("=== trajetos deterministicos (seed) ===")
    for seed in (1, 2, 3, 4):
        print(f"seed={seed} -> {mostrar_trajeto(graph, 'Pedido: ', seed)}")

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
