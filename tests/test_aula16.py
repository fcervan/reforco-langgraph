from src.aula16_paralelo import Estado, sorting_reducer
from langgraph.graph import END, START, StateGraph


def test_simetrico_join_roda_1x():
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
    assert vezes["d"] == 1
    assert sorted(out["itens"]) == ["A", "B", "C", "D"]


def test_desigual_join_dispara_por_chegada():
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
    builder.compile().invoke({"itens": []})
    assert vezes["d"] == 2  # 1x por chegada: ramo curto + ramo longo


def test_sorting_reducer_e_deterministico():
    from typing import Annotated, TypedDict

    class Ord(TypedDict):
        itens: Annotated[list, sorting_reducer]

    builder = StateGraph(Ord)
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
    resultados = [graph.invoke({"itens": []})["itens"] for _ in range(3)]
    assert all(r == ["abacaxi", "banana", "caqui"] for r in resultados)


def test_rag_paralelo_junta_2_fontes(monkeypatch):
    import src.aula16_paralelo as m

    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    # executa a demo via invoke direto do padrão (2 fontes + síntese Fake)
    from typing import TypedDict
    from operator import add
    from typing import Annotated

    class RAG(TypedDict):
        pergunta: str
        contexto: Annotated[list, add]
        resposta: str

    builder = StateGraph(RAG)
    builder.add_node("f1", lambda s: {"contexto": ["fonte1"]})
    builder.add_node("f2", lambda s: {"contexto": ["fonte2"]})
    builder.add_node("sint", lambda s: {"resposta": f"síntese de {len(s['contexto'])}"})
    builder.add_edge(START, "f1")
    builder.add_edge(START, "f2")
    builder.add_edge("f1", "sint")
    builder.add_edge("f2", "sint")
    builder.add_edge("sint", END)
    out = builder.compile().invoke({"pergunta": "q", "contexto": [], "resposta": ""})
    assert sorted(out["contexto"]) == ["fonte1", "fonte2"]
    assert out["resposta"] == "síntese de 2"
