from src.aula09_schemas_multiplos import (
    build_in_out,
    build_privado,
    build_sem_filtro,
)


def test_privado_viaja_mas_nao_sai():
    out = build_privado().invoke({"subtotal": 100})
    assert out == {"subtotal": 110}
    assert "acrescimo" not in out


def test_privado_existe_no_meio():
    passos = list(build_privado().stream({"subtotal": 100}))
    assert passos[0] == {"calcula_taxa": {"acrescimo": 10}}
    assert passos[1] == {"fecha_conta": {"subtotal": 110}}


def test_in_out_esconde_comanda_e_pedido():
    out = build_in_out().invoke({"pedido": "2 pastéis"})
    assert out == {"conta": "R$ 14 (fechada)"}
    assert "comanda" not in out and "pedido" not in out


def test_sem_filtro_tudo_vaza():
    out = build_sem_filtro().invoke({"pedido": "2 pastéis"})
    assert out == {"pedido": "2 pastéis", "conta": "R$ 14 (fechada)", "comanda": "mesa=12"}


def test_chave_extra_no_input_e_ignorada():
    out = build_in_out().invoke({"pedido": "2 pastéis", "comanda": "inject?"})
    assert out == {"conta": "R$ 14 (fechada)"}
