"""Aula 09 — Schemas múltiplos: API pública enxuta, cozinha completa.

Dois mecanismos que desacoplam o que ENTRA/SAI do que CIRCULA:
1. Estado PRIVADO: um nó escreve num schema que não é o geral
   (anotação de retorno); o valor viaja entre nós mas some da saída.
2. input_schema/output_schema: o grafo recebe só `pergunta`, usa `notas`
   por dentro e devolve só `resposta` (nomes novos; `input=`/`output=` do
   curso estão depreciados desde a v0.5).

Sem LLM nesta aula (100% offline). Execute: python src/aula09_schemas_multiplos.py
"""

import warnings
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

warnings.filterwarnings("ignore")  # cala avisos de API antiga nas demos


class EstadoGeral(TypedDict):
    foo: int


class EstadoPrivado(TypedDict):
    baz: int


class Entrada(TypedDict):
    pergunta: str


class Saida(TypedDict):
    resposta: str


class EstadoCompleto(TypedDict):
    pergunta: str
    resposta: str
    notas: str


def build_privado():
    def no_1(estado: EstadoGeral) -> EstadoPrivado:
        return {"baz": estado["foo"] * 10}  # escreve no PRIVADO

    def no_2(estado: EstadoPrivado) -> EstadoGeral:
        return {"foo": estado["baz"] + 1}  # lê o privado, devolve geral

    builder = StateGraph(EstadoGeral)
    builder.add_node("no_1", no_1)
    builder.add_node("no_2", no_2)
    builder.add_edge(START, "no_1")
    builder.add_edge("no_1", "no_2")
    builder.add_edge("no_2", END)
    return builder.compile()


def build_in_out():
    def pensa(estado: EstadoCompleto) -> dict:
        return {"resposta": "tchau", "notas": "nome=Anderson"}

    def responde(estado: EstadoCompleto) -> dict:
        return {"resposta": estado["resposta"] + "!"}

    builder = StateGraph(EstadoCompleto, input_schema=Entrada, output_schema=Saida)
    builder.add_node("pensa", pensa)
    builder.add_node("responde", responde)
    builder.add_edge(START, "pensa")
    builder.add_edge("pensa", "responde")
    builder.add_edge("responde", END)
    return builder.compile()


def build_sem_filtro():
    """Mesmo grafo SEM input/output: tudo vaza na saída (contraste)."""

    def pensa(estado: EstadoCompleto) -> dict:
        return {"resposta": "tchau", "notas": "nome=Anderson"}

    def responde(estado: EstadoCompleto) -> dict:
        return {"resposta": estado["resposta"] + "!"}

    builder = StateGraph(EstadoCompleto)
    builder.add_node("pensa", pensa)
    builder.add_node("responde", responde)
    builder.add_edge(START, "pensa")
    builder.add_edge("pensa", "responde")
    builder.add_edge("responde", END)
    return builder.compile()


def demo_privado() -> None:
    graph = build_privado()
    print("stream (baz existe NO MEIO):")
    for passo in graph.stream({"foo": 1}):
        print("  ", passo)
    out = graph.invoke({"foo": 1})
    print("invoke (saída final):", out, "| 'baz' vazou?", "baz" in out)


def demo_in_out() -> None:
    print("sem filtro :", build_sem_filtro().invoke({"pergunta": "oi"}))
    print("com filtro :", build_in_out().invoke({"pergunta": "oi"}))


def main() -> None:
    print("=== 1. estado privado (baz viaja, não sai) ===")
    demo_privado()
    print("\n=== 2. input/output schemas (notas escondidas) ===")
    demo_in_out()


if __name__ == "__main__":
    main()
