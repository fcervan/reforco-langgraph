import os

import pytest

from src.aula19_mapreduce import build_graph, demo


def _entrada(pedido: str) -> dict:
    return {"pedido": pedido, "itens": [], "avaliacoes": [], "melhor": ""}


def test_map_gera_um_send_por_item(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    chunks = list(build_graph().stream(_entrada("pastel+refri+suco")))
    chaves = [list(c.keys()) for c in chunks]
    assert chaves[0] == ["separa"]
    assert chaves.count(["avalia"]) == 3  # N dinâmico: 3 itens, 3 execuções
    assert chaves[-1] == ["elege"]


def test_reduce_acumula_e_elege(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    out = build_graph().invoke(_entrada("pastel+refri+suco"))
    assert sorted(out["avaliacoes"]) == ["pastel=9", "refri=7", "suco=8"]
    assert out["melhor"] == "pastel=9"


def test_n_varia_com_pedido(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    out = demo("pastel")
    assert out["avaliacoes"] == ["pastel=9"]
    assert out["melhor"] == "pastel=9"


def test_send_import_novo_sem_deprecation():
    import warnings

    from langgraph.types import Send

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # qualquer aviso vira erro
        assert Send("avalia", {"item": "x"})


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="só com chave real")
def test_groq_estruturado_avalia():
    from src.aula19_mapreduce import avalia_item

    texto = avalia_item("pastel")
    nome, nota = texto.split("=")
    assert 0 <= int(nota) <= 10, texto
