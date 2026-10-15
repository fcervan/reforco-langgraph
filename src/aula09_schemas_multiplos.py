"""Aula 09 — Schemas múltiplos: API pública enxuta, cozinha completa.

Dois mecanismos que desacoplam o que ENTRA/SAI do que CIRCULA:
1. Estado PRIVADO: um nó escreve num schema que não é o geral
   (anotação de retorno); o valor viaja entre nós mas some da saída.
2. input_schema/output_schema: o grafo recebe só `pedido`, usa `comanda`
   por dentro e devolve só `conta` (nomes novos; `input=`/`output=`
   emitem aviso de depreciação desde a v0.5).

Sem LLM nesta aula (100% offline). Execute: python src/aula09_schemas_multiplos.py
"""

import warnings
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

warnings.filterwarnings("ignore")  # cala avisos de API antiga nas demos


class ContaGeral(TypedDict):
    subtotal: int


class TaxaPrivada(TypedDict):
    acrescimo: int


class PedidoEntrada(TypedDict):
    pedido: str


class ContaSaida(TypedDict):
    conta: str


class ContaCompleta(TypedDict):
    pedido: str
    conta: str
    comanda: str


def build_privado():
    def calcula_taxa(estado: ContaGeral) -> TaxaPrivada:
        return {"acrescimo": estado["subtotal"] // 10}  # escreve no PRIVADO

    def fecha_conta(estado: TaxaPrivada) -> ContaGeral:
        return {"subtotal": estado["acrescimo"] * 11}  # lê o privado, devolve geral

    builder = StateGraph(ContaGeral)
    builder.add_node("calcula_taxa", calcula_taxa)
    builder.add_node("fecha_conta", fecha_conta)
    builder.add_edge(START, "calcula_taxa")
    builder.add_edge("calcula_taxa", "fecha_conta")
    builder.add_edge("fecha_conta", END)
    return builder.compile()


def build_in_out():
    def anota(estado: ContaCompleta) -> dict:
        return {"conta": "R$ 14", "comanda": "mesa=12"}

    def finaliza(estado: ContaCompleta) -> dict:
        return {"conta": estado["conta"] + " (fechada)"}

    builder = StateGraph(ContaCompleta, input_schema=PedidoEntrada, output_schema=ContaSaida)
    builder.add_node("anota", anota)
    builder.add_node("finaliza", finaliza)
    builder.add_edge(START, "anota")
    builder.add_edge("anota", "finaliza")
    builder.add_edge("finaliza", END)
    return builder.compile()


def build_sem_filtro():
    """Mesmo grafo SEM input/output: tudo vaza na saída (contraste)."""

    def anota(estado: ContaCompleta) -> dict:
        return {"conta": "R$ 14", "comanda": "mesa=12"}

    def finaliza(estado: ContaCompleta) -> dict:
        return {"conta": estado["conta"] + " (fechada)"}

    builder = StateGraph(ContaCompleta)
    builder.add_node("anota", anota)
    builder.add_node("finaliza", finaliza)
    builder.add_edge(START, "anota")
    builder.add_edge("anota", "finaliza")
    builder.add_edge("finaliza", END)
    return builder.compile()


def demo_privado() -> None:
    graph = build_privado()
    print("stream (acrescimo existe NO MEIO):")
    for passo in graph.stream({"subtotal": 100}):
        print("  ", passo)
    out = graph.invoke({"subtotal": 100})
    print("invoke (saída final):", out, "| 'acrescimo' vazou?", "acrescimo" in out)


def demo_in_out() -> None:
    print("sem filtro :", build_sem_filtro().invoke({"pedido": "2 pastéis"}))
    print("com filtro :", build_in_out().invoke({"pedido": "2 pastéis"}))


def main() -> None:
    print("=== 1. estado privado (acrescimo viaja, não sai) ===")
    demo_privado()
    print("\n=== 2. input/output schemas (comanda escondida) ===")
    demo_in_out()


if __name__ == "__main__":
    main()
