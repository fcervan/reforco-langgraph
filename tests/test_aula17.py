import pytest
from langgraph.errors import InvalidUpdateError

from src.aula17_subgrafos import (
    Salao,
    SoBebida,
    SoPrato,
    demo_ingenuo_quebra,
    demo_output_schema_limpo,
    demo_reducer_duplica,
    filho_bar,
    filho_cozinha,
)


def _pai(filho_a, filho_b, schema=Salao):
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(schema)
    builder.add_node("cozinha", filho_a)
    builder.add_node("bar", filho_b)
    builder.add_edge(START, "cozinha")
    builder.add_edge(START, "bar")
    builder.add_edge("cozinha", END)
    builder.add_edge("bar", END)
    return builder.compile()


def _entrada():
    return {"pedido": "pastel", "prato": "", "bebida": "", "conta": ""}


def test_filho_escreve_estado_final_completo():
    """O nó-filho devolve TUDO (inclusive eco da entrada), não só o novo."""
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(Salao)
    builder.add_node("cozinha", filho_cozinha())
    builder.add_edge(START, "cozinha")
    builder.add_edge("cozinha", END)
    out = builder.compile().invoke(_entrada())
    assert out["prato"] == "prato(pastel)"
    assert out["pedido"] == "pastel"  # eco da entrada voltou junto


def test_dois_filhos_quebram_na_chave_comum():
    with pytest.raises(InvalidUpdateError):
        _pai(filho_cozinha(), filho_bar()).invoke(_entrada())


def test_reducer_evita_crash_mas_duplica():
    from typing import Annotated, TypedDict
    from operator import add

    class SalaoAdd(TypedDict):
        pedido: Annotated[str, add]
        prato: str
        bebida: str
        conta: str

    out = _pai(filho_cozinha(), filho_bar(), schema=SalaoAdd).invoke(_entrada())
    assert out["pedido"] == "pastelpastelpastel"


def test_output_schema_e_cirurgico():
    out = _pai(
        filho_cozinha(output_schema=SoPrato), filho_bar(output_schema=SoBebida)
    ).invoke(_entrada())
    assert out["pedido"] == "pastel"
    assert out["prato"] == "prato(pastel)"
    assert out["bebida"] == "bebida(pastel)"
    assert "rascunho" not in out  # privado do filho não vaza


def test_demos_rodam(capsys):
    demo_ingenuo_quebra()
    demo_reducer_duplica()
    demo_output_schema_limpo()
    saida = capsys.readouterr().out
    assert "InvalidUpdateError" in saida
    assert "pastelpastelpastel" in saida
    assert "prato(pastel)" in saida
