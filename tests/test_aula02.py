import random

from src.aula02_grafo import build_graph, decide_mood, node_1, node_2


def test_nodes_concatenam():
    assert node_1({"graph_state": "Oi,"}) == {"graph_state": "Oi, Eu estou "}
    assert node_2({"graph_state": "X"}) == {"graph_state": "Xcansado!"}


def test_grafo_roda():
    random.seed(1)
    out = build_graph().invoke({"graph_state": "Oi,"})
    assert out["graph_state"].startswith("Oi, Eu estou ")
    assert out["graph_state"] in ("Oi, Eu estou cansado!", "Oi, Eu estou descansado!")


def test_decide_mood_retorna_no_valido():
    random.seed(0)
    assert decide_mood({"graph_state": "x"}) in ("node_2", "node_3")
