"""Aula 17 — Sub-grafos: grafos dentro de grafos.

Um sub-grafo compilado vira NÓ do pai (`add_node("x", filho.compile())`):
- o filho LÊ as chaves do pai que existem no schema dele;
- o filho ESCREVE DE VOLTA o estado final COMPLETO (inclusive ecoando a
  entrada!) — dois filhos paralelos com chave de entrada comum QUEBRAM
  (InvalidUpdateError), a menos que...
- ...o pai ponha reducer na chave (funciona, mas duplica o eco), ou
- ...o filho declare `output_schema` (cirúrgico: só essas chaves voltam).

Sem LLM nesta aula (100% offline). Execute: python src/aula17_subgrafos.py
"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph


class Cozinha(TypedDict):
    pedido: str
    prato: str
    rascunho: str


class Bar(TypedDict):
    pedido: str
    bebida: str


class SoPrato(TypedDict):
    prato: str


class SoBebida(TypedDict):
    bebida: str


class Salao(TypedDict):
    pedido: str
    prato: str
    bebida: str
    conta: str


def filho_cozinha(output_schema=None):
    builder = StateGraph(Cozinha, **({"output_schema": output_schema} if output_schema else {}))

    def cozinhar(state: Cozinha) -> dict:
        return {"prato": f"prato({state['pedido']})", "rascunho": "anotação interna"}

    builder.add_node("cozinhar", cozinhar)
    builder.add_edge(START, "cozinhar")
    builder.add_edge("cozinhar", END)
    return builder.compile()


def filho_bar(output_schema=None):
    builder = StateGraph(Bar, **({"output_schema": output_schema} if output_schema else {}))
    builder.add_node("servir", lambda s: {"bebida": f"bebida({s['pedido']})"})
    builder.add_edge(START, "servir")
    builder.add_edge("servir", END)
    return builder.compile()


def demo_ingenuo_quebra() -> None:
    """Dois filhos ecoam 'pedido' na mesma etapa -> InvalidUpdateError."""
    builder = StateGraph(Salao)
    builder.add_node("cozinha", filho_cozinha())
    builder.add_node("bar", filho_bar())
    builder.add_edge(START, "cozinha")
    builder.add_edge(START, "bar")
    builder.add_edge("cozinha", END)
    builder.add_edge("bar", END)
    try:
        builder.compile().invoke({"pedido": "pastel", "prato": "", "bebida": "", "conta": ""})
    except InvalidUpdateError as erro:
        print("ingênuo -> InvalidUpdateError:")
        print("  ", str(erro).split("\n")[0])
        print("  (cada filho devolveu 'pedido' junto: eco duplo na mesma etapa)")


def demo_reducer_duplica() -> None:
    """Reducer na chave comum evita o crash, mas o eco duplica o valor."""

    class SalaoAdd(TypedDict):
        pedido: Annotated[str, add]
        prato: str
        bebida: str
        conta: str

    builder = StateGraph(SalaoAdd)
    builder.add_node("cozinha", filho_cozinha())
    builder.add_node("bar", filho_bar())
    builder.add_edge(START, "cozinha")
    builder.add_edge(START, "bar")
    builder.add_edge("cozinha", END)
    builder.add_edge("bar", END)
    out = builder.compile().invoke({"pedido": "pastel", "prato": "", "bebida": "", "conta": ""})
    print("reducer -> pedido =", repr(out["pedido"]), "(eco triplicado: original + 2 filhos)")


def demo_output_schema_limpo() -> None:
    """output_schema no filho: só as chaves declaradas voltam ao pai."""
    builder = StateGraph(Salao)
    builder.add_node("cozinha", filho_cozinha(output_schema=SoPrato))
    builder.add_node("bar", filho_bar(output_schema=SoBebida))
    builder.add_node("fechar", lambda s: {"conta": f"{s['prato']} + {s['bebida']}"})
    builder.add_edge(START, "cozinha")
    builder.add_edge(START, "bar")
    builder.add_edge("cozinha", "fechar")
    builder.add_edge("bar", "fechar")
    builder.add_edge("fechar", END)
    out = builder.compile().invoke({"pedido": "pastel", "prato": "", "bebida": "", "conta": ""})
    print("output_schema ->", out)
    print("  (pedido intacto, rascunho não vazou, conta fechada no pai)")


def main() -> None:
    print("=== 1. ingênuo: eco duplo quebra ===")
    demo_ingenuo_quebra()
    print("\n=== 2. reducer: não quebra, mas duplica ===")
    demo_reducer_duplica()
    print("\n=== 3. output_schema: cirúrgico ===")
    demo_output_schema_limpo()


if __name__ == "__main__":
    main()
