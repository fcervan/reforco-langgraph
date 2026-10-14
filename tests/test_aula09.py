from src.aula09_schemas_multiplos import (
    build_in_out,
    build_privado,
    build_sem_filtro,
)


def test_privado_viaja_mas_nao_sai():
    out = build_privado().invoke({"foo": 1})
    assert out == {"foo": 11}
    assert "baz" not in out


def test_privado_existe_no_meio():
    passos = list(build_privado().stream({"foo": 1}))
    assert passos[0] == {"no_1": {"baz": 10}}
    assert passos[1] == {"no_2": {"foo": 11}}


def test_in_out_esconde_notas_e_pergunta():
    out = build_in_out().invoke({"pergunta": "oi"})
    assert out == {"resposta": "tchau!"}
    assert "notas" not in out and "pergunta" not in out


def test_sem_filtro_tudo_vaza():
    out = build_sem_filtro().invoke({"pergunta": "oi"})
    assert out == {"pergunta": "oi", "resposta": "tchau!", "notas": "nome=Anderson"}


def test_chave_extra_no_input_e_ignorada():
    out = build_in_out().invoke({"pergunta": "oi", "notas": "inject?"})
    assert out == {"resposta": "tchau!"}
