"""Aula 07 — Schemas de estado: contrato do dict compartilhado.

O mesmo grafo (no_nome/no_satisfeito/no_insatisfeito + decide) com 3 contratos diferentes:
- TypedDict: só dica de tipo — "confuso" entra calado.
- dataclass: acesso por atributo (`state.name`) — "confuso" entra calado.
- Pydantic: VALIDA de verdade — "confuso" morre com ValidationError.

Sem LLM nesta aula (100% offline). Execute: python src/aula07_schemas.py
"""

import random
from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ValidationError, field_validator


class TDState(TypedDict):
    name: str
    mood: Literal["satisfeito", "insatisfeito"]


@dataclass
class DCState:
    name: str
    mood: Literal["satisfeito", "insatisfeito"]


class PYState(BaseModel):
    name: str
    mood: Literal["satisfeito", "insatisfeito"]

    @field_validator("mood")
    @classmethod
    def checa_humor(cls, valor: str) -> str:
        # Roda DEPOIS do Literal: serve para regras extras (ex: normalizar).
        # "confuso" nem chega aqui — o Literal barra antes.
        return valor.strip().lower()


def montar_td():
    def no_nome(state: TDState) -> dict:
        return {"name": state["name"] + " está ... "}

    def no_satisfeito(state: TDState) -> dict:
        return {"mood": "satisfeito"}

    def no_insatisfeito(state: TDState) -> dict:
        return {"mood": "insatisfeito"}

    builder = StateGraph(TDState)
    builder.add_node("no_nome", no_nome)
    builder.add_node("no_satisfeito", no_satisfeito)
    builder.add_node("no_insatisfeito", no_insatisfeito)
    builder.add_edge(START, "no_nome")
    builder.add_conditional_edges("no_nome", lambda s: "no_satisfeito" if random.random() < 0.5 else "no_insatisfeito")
    builder.add_edge("no_satisfeito", END)
    builder.add_edge("no_insatisfeito", END)
    return builder.compile()


def montar_dc():
    def no_nome(state: DCState) -> dict:
        return {"name": state.name + " está ... "}  # atributo, não ["chave"]

    def no_satisfeito(state: DCState) -> dict:
        return {"mood": "satisfeito"}

    def no_insatisfeito(state: DCState) -> dict:
        return {"mood": "insatisfeito"}

    builder = StateGraph(DCState)
    builder.add_node("no_nome", no_nome)
    builder.add_node("no_satisfeito", no_satisfeito)
    builder.add_node("no_insatisfeito", no_insatisfeito)
    builder.add_edge(START, "no_nome")
    builder.add_conditional_edges("no_nome", lambda s: "no_satisfeito" if random.random() < 0.5 else "no_insatisfeito")
    builder.add_edge("no_satisfeito", END)
    builder.add_edge("no_insatisfeito", END)
    return builder.compile()


def montar_py():
    def no_nome(state: PYState) -> dict:
        return {"name": state.name + " está ... "}  # instância BaseModel

    def no_satisfeito(state: PYState) -> dict:
        return {"mood": "satisfeito"}

    def no_insatisfeito(state: PYState) -> dict:
        return {"mood": "insatisfeito"}

    builder = StateGraph(PYState)
    builder.add_node("no_nome", no_nome)
    builder.add_node("no_satisfeito", no_satisfeito)
    builder.add_node("no_insatisfeito", no_insatisfeito)
    builder.add_edge(START, "no_nome")
    builder.add_conditional_edges("no_nome", lambda s: "no_satisfeito" if random.random() < 0.5 else "no_insatisfeito")
    builder.add_edge("no_satisfeito", END)
    builder.add_edge("no_insatisfeito", END)
    return builder.compile()


def demo_confuso() -> None:
    """O mesmo valor inválido nos 3 schemas: só o Pydantic barra."""
    print("TypedDict + confuso  ->", montar_td().invoke({"name": "Rafa", "mood": "confuso"}),
          "(entrou calado)")
    print("dataclass + confuso  ->", montar_dc().invoke(DCState(name="Rafa", mood="confuso")),
          "(entrou calado)")
    try:
        PYState(name="Rafa", mood="confuso")
    except ValidationError as erro:
        print("Pydantic + confuso   -> ValidationError:")
        print("   " + str(erro).split("\n")[1].strip())


def demo_valido() -> None:
    random.seed(1)
    print("TypedDict válido   ->", montar_td().invoke({"name": "Rafa", "mood": "insatisfeito"}))
    print("dataclass válido   ->", montar_dc().invoke(DCState(name="Rafa", mood="insatisfeito")))
    print("Pydantic válido    ->", montar_py().invoke(PYState(name="Rafa", mood="insatisfeito")))


def main() -> None:
    print("=== 'confuso' nos 3 schemas ===")
    demo_confuso()
    print("\n=== valores válidos ===")
    demo_valido()


if __name__ == "__main__":
    main()
