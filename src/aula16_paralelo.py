"""Aula 16 — Paralelização: fan-out/fan-in de verdade.

- Fan-out simétrico (b e c na mesma profundidade): o join roda 1x.
- Fan-out desigual (b->b2 vs c): o join roda 1x POR CHEGADA (2x!).
- Reducer decide a mesclagem; sorting_reducer dá ordem determinística.
- RAG paralelo: 2 fontes simultâneas + 1 síntese (mais rápido que em série).

Sem LLM obrigatório: demos 1-4 offline; RAG usa Groq com chave, Fake sem.
Execute: python src/aula16_paralelo.py
"""

from operator import add
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

load_dotenv()


class Estado(TypedDict):
    itens: Annotated[list, add]


def sorting_reducer(esquerda, direita):
    """Mescla e ORDENA: ordem determinística independente de quem chegou antes."""
    if not isinstance(esquerda, list):
        esquerda = [esquerda]
    if not isinstance(direita, list):
        direita = [direita]
    return sorted(esquerda + direita)


class EstadoOrdenado(TypedDict):
    itens: Annotated[list, sorting_reducer]


def demo_simetrico_roda_1x() -> None:
    """b e c na mesma profundidade: d espera os dois e roda 1x."""
    vezes = {"d": 0}

    def d(state: Estado) -> dict:
        vezes["d"] += 1
        return {"itens": ["D"]}

    builder = StateGraph(Estado)
    builder.add_node("a", lambda s: {"itens": ["A"]})
    builder.add_node("b", lambda s: {"itens": ["B"]})
    builder.add_node("c", lambda s: {"itens": ["C"]})
    builder.add_node("d", d)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("a", "c")
    builder.add_edge("b", "d")
    builder.add_edge("c", "d")
    builder.add_edge("d", END)
    out = builder.compile().invoke({"itens": []})
    print("simétrico:", out["itens"], f"| d rodou {vezes['d']}x")


def demo_desigual_dispara_2x() -> None:
    """b->b2 (longo) vs c (curto): d dispara 1x POR CHEGADA (2x)."""
    vezes = {"d": 0}

    def d(state: Estado) -> dict:
        vezes["d"] += 1
        return {"itens": [f"D{vezes['d']}"]}

    builder = StateGraph(Estado)
    builder.add_node("a", lambda s: {"itens": ["A"]})
    builder.add_node("b", lambda s: {"itens": ["B"]})
    builder.add_node("b2", lambda s: {"itens": ["B2"]})
    builder.add_node("c", lambda s: {"itens": ["C"]})
    builder.add_node("d", d)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("a", "c")
    builder.add_edge("b", "b2")
    builder.add_edge("b2", "d")
    builder.add_edge("c", "d")
    builder.add_edge("d", END)
    out = builder.compile().invoke({"itens": []})
    print("desigual:", out["itens"], f"| d rodou {vezes['d']}x (1x por chegada!)")


def demo_sorting() -> None:
    """sorting_reducer: mesma saída nas 3 execuções, independente da ordem."""
    builder = StateGraph(EstadoOrdenado)
    builder.add_node("x", lambda s: {"itens": ["banana"]})
    builder.add_node("y", lambda s: {"itens": ["abacaxi"]})
    builder.add_node("z", lambda s: {"itens": ["caqui"]})
    builder.add_edge(START, "x")
    builder.add_edge(START, "y")
    builder.add_edge(START, "z")
    builder.add_edge("x", END)
    builder.add_edge("y", END)
    builder.add_edge("z", END)
    graph = builder.compile()
    for i in range(3):
        print(f"sorting #{i + 1}:", graph.invoke({"itens": []})["itens"])


def demo_rag_paralelo() -> None:
    """2 fontes simultâneas + 1 síntese (padrão RAG paralelo sem APIs externas)."""
    import os

    class RAG(TypedDict):
        pergunta: str
        contexto: Annotated[list, add]
        resposta: str

    def fonte_cardapio(state: RAG) -> dict:
        return {"contexto": ["cardápio: pastel R$ 8, refri R$ 6"]}

    def fonte_promocao(state: RAG) -> dict:
        return {"contexto": ["promoção: 2 pastéis por R$ 14"]}

    def sintetiza(state: RAG) -> dict:
        if os.getenv("GROQ_API_KEY"):
            try:
                from langchain_groq import ChatGroq

                llm = ChatGroq(
                    model="openai/gpt-oss-20b", temperature=0, reasoning_effort="low"
                )
                r = llm.invoke(
                    f"Com este contexto: {state['contexto']}. Responda: {state['pergunta']}"
                )
                return {"resposta": r.content}
            except ImportError:
                pass
        return {"resposta": f"síntese (Fake) de {len(state['contexto'])} fontes"}

    builder = StateGraph(RAG)
    builder.add_node("cardapio", fonte_cardapio)
    builder.add_node("promocao", fonte_promocao)
    builder.add_node("sintetiza", sintetiza)
    builder.add_edge(START, "cardapio")
    builder.add_edge(START, "promocao")
    builder.add_edge("cardapio", "sintetiza")
    builder.add_edge("promocao", "sintetiza")
    builder.add_edge("sintetiza", END)
    out = builder.compile().invoke({"pergunta": "quanto custa 2 pastéis?", "contexto": [], "resposta": ""})
    print("fontes: 2 em paralelo | resposta:", repr(out["resposta"])[:90])


def main() -> None:
    print("=== 1. fan-out simétrico: join roda 1x ===")
    demo_simetrico_roda_1x()
    print("\n=== 2. fan-out desigual: join dispara 2x ===")
    demo_desigual_dispara_2x()
    print("\n=== 3. sorting_reducer: ordem determinística ===")
    demo_sorting()
    print("\n=== 4. RAG paralelo: 2 fontes + síntese ===")
    demo_rag_paralelo()


if __name__ == "__main__":
    main()
