import random
from typing import TypedDict

import pytest

from src.aula02_grafo import (
    State,
    build_graph,
    decide_mood,
    demo_chave_fora_do_schema,
    demo_overwrite,
    demo_rota_inexistente,
    node_1,
    node_2,
)


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


def test_seed_deixa_deterministico():
    """Mesma seed => mesmo caminho."""
    random.seed(7)
    a = build_graph().invoke({"graph_state": "Oi,"})["graph_state"]
    random.seed(7)
    b = build_graph().invoke({"graph_state": "Oi,"})["graph_state"]
    assert a == b


def test_input_incompleto_da_keyerror():
    """Faltou a chave do estado: o erro so aparece quando UM NO le a chave."""
    with pytest.raises(KeyError):
        build_graph().invoke({"outra_coisa": "x"})


def test_overwrite_ultimo_no_ganha(capsys):
    demo_overwrite()
    saida = capsys.readouterr().out
    assert "escrito por B" in saida and "inicial" not in saida


def test_chave_fora_do_schema_e_ignorada(capsys):
    demo_chave_fora_do_schema(build_graph())
    saida = capsys.readouterr().out
    assert "valor original" in saida and "nao_existe" not in saida


def test_rota_inexistente_encerra_sem_excecao(capsys):
    graph = build_graph()
    demo_rota_inexistente(graph)
    saida = capsys.readouterr().out
    # node_1 rodou, mas node_2/node_3 nunca (nenhum dos dois sufixos aparece)
    assert "Oi, Eu estou " in saida
    assert "cansado" not in saida and "descansado" not in saida


def test_mermaid_lista_nos():
    mermaid = build_graph().get_graph().draw_mermaid()
    for no in ("node_1", "node_2", "node_3"):
        assert no in mermaid


def test_aresta_para_no_inexistente_da_valueerror():
    from langgraph.graph import START, StateGraph

    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_edge(START, "node_1")
    with pytest.raises(ValueError):
        builder.add_edge("node_1", "fantasma")
        builder.compile()


def test_no_sem_argumento_da_typeerror():
    from langgraph.graph import END, START, StateGraph

    def sem_arg():
        return {}

    builder = StateGraph(State)
    builder.add_node("x", sem_arg)
    builder.add_edge(START, "x")
    builder.add_edge("x", END)
    with pytest.raises(TypeError):
        builder.compile().invoke({"graph_state": "x"})
