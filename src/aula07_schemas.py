"""Aula 07 — Schemas de estado: contrato do dict compartilhado.

O mesmo grafo (node_1/node_2/node_3 + decide) com 3 contratos diferentes:
- TypedDict: só dica de tipo — "bravo" entra calado.
- dataclass: acesso por atributo (`state.name`) — "bravo" entra calado.
- Pydantic: VALIDA de verdade — "bravo" morre com ValidationError.

Sem LLM nesta aula (100% offline). Execute: python src/aula07_schemas.py
"""

import random
from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ValidationError, field_validator


class TDState(TypedDict):
    name: str
    mood: Literal["feliz", "triste"]


@dataclass
class DCState:
    name: str
    mood: Literal["feliz", "triste"]


class PYState(BaseModel):
    name: str
    mood: Literal["feliz", "triste"]

    @field_validator("mood")
    @classmethod
    def checa_humor(cls, valor: str) -> str:
        # Roda DEPOIS do Literal: serve para regras extras (ex: normalizar).
        # "bravo" nem chega aqui — o Literal barra antes.
        return valor.strip().lower()


def montar_td():
    def node_1(state: TDState) -> dict:
        return {"name": state["name"] + " está ... "}

    def node_2(state: TDState) -> dict:
        return {"mood": "feliz"}

    def node_3(state: TDState) -> dict:
        return {"mood": "triste"}

    builder = StateGraph(TDState)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", lambda s: "node_2" if random.random() < 0.5 else "node_3")
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    return builder.compile()


def montar_dc():
    def node_1(state: DCState) -> dict:
        return {"name": state.name + " está ... "}  # atributo, não ["chave"]

    def node_2(state: DCState) -> dict:
        return {"mood": "feliz"}

    def node_3(state: DCState) -> dict:
        return {"mood": "triste"}

    builder = StateGraph(DCState)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", lambda s: "node_2" if random.random() < 0.5 else "node_3")
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    return builder.compile()


def montar_py():
    def node_1(state: PYState) -> dict:
        return {"name": state.name + " está ... "}  # instância BaseModel

    def node_2(state: PYState) -> dict:
        return {"mood": "feliz"}

    def node_3(state: PYState) -> dict:
        return {"mood": "triste"}

    builder = StateGraph(PYState)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", lambda s: "node_2" if random.random() < 0.5 else "node_3")
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)
    return builder.compile()


def demo_bravo() -> None:
    """O mesmo valor inválido nos 3 schemas: só o Pydantic barra."""
    print("TypedDict + bravo  ->", montar_td().invoke({"name": "Zé", "mood": "bravo"}),
          "(entrou calado)")
    print("dataclass + bravo  ->", montar_dc().invoke(DCState(name="Zé", mood="bravo")),
          "(entrou calado)")
    try:
        PYState(name="Zé", mood="bravo")
    except ValidationError as erro:
        print("Pydantic + bravo   -> ValidationError:")
        print("   " + str(erro).split("\n")[1].strip())


def demo_valido() -> None:
    random.seed(1)
    print("TypedDict válido   ->", montar_td().invoke({"name": "Zé", "mood": "triste"}))
    print("dataclass válido   ->", montar_dc().invoke(DCState(name="Zé", mood="triste")))
    print("Pydantic válido    ->", montar_py().invoke(PYState(name="Zé", mood="triste")))


def main() -> None:
    print("=== 'bravo' nos 3 schemas ===")
    demo_bravo()
    print("\n=== valores válidos ===")
    demo_valido()


if __name__ == "__main__":
    main()
