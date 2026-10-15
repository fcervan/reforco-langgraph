import random
from typing import TypedDict

import pytest

from src.aula02_grafo import (
    State,
    build_graph,
    decide_bebida,
    demo_chave_fora_do_schema,
    demo_overwrite,
    demo_rota_inexistente,
    no_recebe,
    no_suco,
)


def test_nodes_concatenam():
    assert no_recebe({"pedido": "Pedido: "}) == {"pedido": "Pedido: hamburguer"}
    assert no_suco({"pedido": "X"}) == {"pedido": "X + suco"}


def test_grafo_roda():
    random.seed(1)
    out = build_graph().invoke({"pedido": "Pedido: "})
    assert out["pedido"].startswith("Pedido: hamburguer")
    assert out["pedido"] in ("Pedido: hamburguer + suco", "Pedido: hamburguer + água")


def test_decide_bebida_retorna_no_valido():
    random.seed(0)
    assert decide_bebida({"pedido": "x"}) in ("no_suco", "no_agua")


def test_seed_deixa_deterministico():
    """Mesma seed => mesmo caminho."""
    random.seed(7)
    a = build_graph().invoke({"pedido": "Pedido: "})["pedido"]
    random.seed(7)
    b = build_graph().invoke({"pedido": "Pedido: "})["pedido"]
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
    # no_recebe rodou, mas no_suco/no_agua nunca (nenhum dos dois sufixos aparece)
    assert "Pedido: hamburguer" in saida
    assert " + suco" not in saida and " + água" not in saida


def test_mermaid_lista_nos():
    mermaid = build_graph().get_graph().draw_mermaid()
    for no in ("no_recebe", "no_suco", "no_agua"):
        assert no in mermaid


def test_aresta_para_no_inexistente_da_valueerror():
    from langgraph.graph import START, StateGraph

    builder = StateGraph(State)
    builder.add_node("no_recebe", no_recebe)
    builder.add_edge(START, "no_recebe")
    with pytest.raises(ValueError):
        builder.add_edge("no_recebe", "fantasma")
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
        builder.compile().invoke({"pedido": "x"})
