"""Aula 00 — Visão Geral (espelho executável do notebook).

Sem LLM, sem chave, 100% offline. O mesmo exemplo da lanchonete
nas duas versões: (A) Python clássico e (B) LangGraph.
Execute: python src/aula00_visao_geral.py
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

# ============================================================
# Versão A — Python clássico (o que você já domina)
# Estado = dict. Etapa = função. Fluxo = if/else.
# ============================================================


def receber_pedido(pedido: dict) -> dict:
    pedido["itens"].append("hamburguer")
    return pedido


def escolher_bebida(pedido: dict) -> dict:
    if pedido.get("com_sede"):
        pedido["itens"].append("suco")
    else:
        pedido["itens"].append("agua")
    return pedido


def versao_classica(com_sede: bool) -> dict:
    pedido = {"itens": [], "com_sede": com_sede}
    pedido = receber_pedido(pedido)
    pedido = escolher_bebida(pedido)
    return pedido


# ============================================================
# Versão B — O MESMO fluxo em LangGraph
# Nó = função(state) -> update parcial. Aresta = ordem.
# ============================================================


class Pedido(TypedDict):
    itens: list
    com_sede: bool


def no_receber(state: Pedido) -> dict:
    # Note: devolvemos SÓ o que mudou, não o dict inteiro.
    return {"itens": state["itens"] + ["hamburguer"]}


def no_bebida_com_sede(state: Pedido) -> dict:
    return {"itens": state["itens"] + ["suco"]}


def no_bebida_sem_sede(state: Pedido) -> dict:
    return {"itens": state["itens"] + ["agua"]}


def decide_bebida(state: Pedido) -> str:
    # Aresta condicional = o seu if, com outro nome.
    return "com_sede" if state["com_sede"] else "sem_sede"


def build_graph():
    builder = StateGraph(Pedido)
    builder.add_node("receber", no_receber)
    builder.add_node("com_sede", no_bebida_com_sede)
    builder.add_node("sem_sede", no_bebida_sem_sede)
    builder.add_edge(START, "receber")
    builder.add_conditional_edges("receber", decide_bebida)
    builder.add_edge("com_sede", END)
    builder.add_edge("sem_sede", END)
    return builder.compile()


def main() -> None:
    print("A (classico):", versao_classica(com_sede=True)["itens"])
    graph = build_graph()
    print("B (grafo)   :", graph.invoke({"itens": [], "com_sede": True})["itens"])
    print("B (grafo)   :", graph.invoke({"itens": [], "com_sede": False})["itens"])
    print("\nMesmo resultado. O grafo só organiza o que o if já fazia.")


if __name__ == "__main__":
    main()
