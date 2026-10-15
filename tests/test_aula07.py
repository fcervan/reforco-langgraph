import random

import pytest
from pydantic import BaseModel, ValidationError, field_validator

from src.aula07_schemas import DCState, PYState, TDState, montar_dc, montar_py, montar_td


def test_typeddict_aceita_confuso_calado():
    """TypedDict é só dica: valor inválido entra sem erro."""
    random.seed(1)
    out = montar_td().invoke({"name": "Rafa", "mood": "confuso"})
    assert out["name"].startswith("Rafa está")
    assert out["mood"] in ("satisfeito", "insatisfeito")  # o nó sobrescreveu; a entrada passou


def test_dataclass_aceita_confuso_calado():
    """Sem nó que sobrescreva, o inválido persiste: ninguém validou."""
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(DCState)
    builder.add_node("passa", lambda s: {})
    builder.add_edge(START, "passa")
    builder.add_edge("passa", END)
    out = builder.compile().invoke(DCState(name="Rafa", mood="confuso"))
    assert out["mood"] == "confuso"  # entrou e ficou: silêncio total


def test_dataclass_usa_acesso_por_atributo():
    vistos = {}

    def sonda(state: DCState) -> dict:
        vistos["tipo"] = type(state).__name__
        vistos["via_atributo"] = state.name
        return {}

    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(DCState)
    builder.add_node("sonda", sonda)
    builder.add_edge(START, "sonda")
    builder.add_edge("sonda", END)
    builder.compile().invoke(DCState(name="Rafa", mood="satisfeito"))
    assert vistos == {"tipo": "DCState", "via_atributo": "Rafa"}


def test_pydantic_barra_confuso():
    with pytest.raises(ValidationError):
        PYState(name="Rafa", mood="confuso")


def test_pydantic_valido_roda():
    random.seed(1)
    out = montar_py().invoke(PYState(name="Rafa", mood="insatisfeito"))
    assert out["name"].startswith("Rafa está")
    assert out["mood"] in ("satisfeito", "insatisfeito")


def test_pydantic_ignora_chave_extra():
    out = montar_py().invoke({"name": "Rafa", "mood": "satisfeito", "extra": 1})
    assert "extra" not in out


def test_validador_custom_normaliza():
    class Norm(BaseModel):
        mood: str

        @field_validator("mood")
        @classmethod
        def limpa(cls, v: str) -> str:
            return v.strip().lower()

    assert Norm(mood="  SATISFEITO ").mood == "satisfeito"


def test_tdstate_e_dict_na_pratica():
    estado: TDState = {"name": "Rafa", "mood": "satisfeito"}
    assert estado["name"] == "Rafa"  # acesso por chave, como dict comum
