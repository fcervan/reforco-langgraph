import os

import pytest

from src.aula01_setup import MODELO, get_llm, tem_chave


def test_get_llm_offline_sem_chave(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    llm, origem = get_llm()
    assert origem == "fake"
    assert not tem_chave()


def test_invoke_retorna_ai_message(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    llm, _ = get_llm()
    resposta = llm.invoke("oi")
    assert type(resposta).__name__ == "AIMessage"
    assert isinstance(resposta.content, str) and resposta.content


def test_stream_soma_igual_invoke(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    llm, _ = get_llm()
    via_invoke = llm.invoke("oi").content
    via_stream = "".join(pedaco.content for pedaco in llm.stream("oi"))
    assert via_stream == via_invoke


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="só com chave real")
def test_groq_real_responde():
    llm, origem = get_llm()
    assert origem == "groq"
    resposta = llm.invoke("Responda só: ok")
    assert "ok" in resposta.content.lower()
    assert MODELO == "openai/gpt-oss-20b"
