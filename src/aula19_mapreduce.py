"""Aula 19 — MapReduce: N tarefas que nascem em runtime (última do curso).

- MAP dinâmico: a condicional devolve lista de `Send("avalia", {...})` — um
  por item, N decidido em runtime (não dá para desenhar N arestas fixas).
- Cada `Send` executa `avalia` com seu sub-estado; os resultados SOMAM via
  `Annotated[list, add]`.
- REDUCE: um nó final lê tudo e elege o melhor.

Com GROQ_API_KEY, a avaliação usa saída estruturada real; sem chave, tabela
local determinística. Execute: python src/aula19_mapreduce.py
"""

import os
from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send  # novo (langgraph.constants.Send depreciado na v1.0)

load_dotenv()

MODELO = "openai/gpt-oss-20b"
NOTAS = {"pastel": 9, "refri": 7, "suco": 8}


class Comanda(TypedDict):
    pedido: str
    itens: list[str]
    avaliacoes: Annotated[list, add]
    melhor: str


class Item(TypedDict):
    item: str


def avalia_item(item: str) -> str:
    """Com Groq: nota estruturada real. Sem chave: tabela local."""
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            from pydantic import BaseModel

            class Avaliacao(BaseModel):
                item: str
                nota: int

            llm = ChatGroq(model=MODELO, temperature=0, reasoning_effort="low")
            r = llm.with_structured_output(Avaliacao).invoke(
                f"Avalie '{item}' da lanchonete com nota de 0 a 10."
            )
            return f"{r.item}={r.nota}"
        except ImportError:
            pass
    return f"{item}={NOTAS.get(item, 5)}"


def build_graph():
    def separa(state: Comanda) -> dict:
        return {"itens": [i.strip() for i in state["pedido"].split("+") if i.strip()]}

    def continua(state: Comanda):
        # MAP dinâmico: um Send por item (N decidido em runtime!)
        return [Send("avalia", {"item": i}) for i in state["itens"]]

    def avalia(state: Item) -> dict:
        return {"avaliacoes": [avalia_item(state["item"])]}

    def elege(state: Comanda) -> dict:
        top = sorted(state["avaliacoes"], key=lambda s: int(s.split("=")[1]), reverse=True)[0]
        return {"melhor": top}

    builder = StateGraph(Comanda)
    builder.add_node("separa", separa)
    builder.add_node("avalia", avalia)
    builder.add_node("elege", elege)
    builder.add_edge(START, "separa")
    builder.add_conditional_edges("separa", continua)
    builder.add_edge("avalia", "elege")
    builder.add_edge("elege", END)
    return builder.compile()


def demo(pedido: str) -> dict:
    graph = build_graph()
    out = graph.invoke({"pedido": pedido, "itens": [], "avaliacoes": [], "melhor": ""})
    print(f"pedido {pedido!r} -> avaliações {out['avaliacoes']} -> melhor {out['melhor']!r}")
    return out


def demo_stream() -> None:
    """O stream mostra N execuções de 'avalia' (uma por Send)."""
    graph = build_graph()
    for chunk in graph.stream(
        {"pedido": "pastel+suco", "itens": [], "avaliacoes": [], "melhor": ""}
    ):
        print("  ", list(chunk.keys()))


def main() -> None:
    print("=== 1. map com N dinâmico + reduce ===")
    demo("pastel+refri+suco")
    demo("pastel")
    print("\n=== 2. stream: um 'avalia' por Send ===")
    demo_stream()


if __name__ == "__main__":
    main()
