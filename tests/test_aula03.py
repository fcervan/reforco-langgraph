from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

from src.aula03_cadeias import build_graph, multiply, soma


def test_multiply_e_soma():
    assert multiply(3, 4) == 12
    assert soma(10, 5) == 15


def test_cadeia_detecta_tool_offline():
    out = build_graph().invoke({"messages": [HumanMessage(content="Quanto é 3 vezes 4?")]})
    ultima = out["messages"][-1]
    assert ultima.tool_calls and ultima.tool_calls[0]["name"] == "multiply"
    assert ultima.tool_calls[0]["args"] == {"a": 3, "b": 4}


def test_tool_call_vem_com_content_vazio_offline():
    """Igual ao gpt-oss real: intenção de tool não traz texto (ver Aula 01, 3.1)."""
    out = build_graph().invoke({"messages": [HumanMessage(content="Quanto é 3 vezes 4?")]})
    ultima = out["messages"][-1]
    assert ultima.content == "" and ultima.tool_calls


def test_sem_reducer_historico_se_perde():
    """Dois nós em sequência SEM add_messages: o 2º apaga o 1º."""
    from typing import TypedDict

    class SemReducer(TypedDict):
        messages: list

    builder = StateGraph(SemReducer)
    builder.add_node("n1", lambda s: {"messages": [HumanMessage(content="pergunta")]})
    builder.add_node("n2", lambda s: {"messages": [AIMessage(content="resposta")]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n2", END)
    out = builder.compile().invoke({"messages": []})
    assert [m.content for m in out["messages"]] == ["resposta"]


def test_com_reducer_historico_acumula():
    builder = StateGraph(MessagesState)
    builder.add_node("n1", lambda s: {"messages": [HumanMessage(content="pergunta")]})
    builder.add_node("n2", lambda s: {"messages": [AIMessage(content="resposta")]})
    builder.add_edge(START, "n1")
    builder.add_edge("n1", "n2")
    builder.add_edge("n2", END)
    out = builder.compile().invoke({"messages": []})
    assert [m.content for m in out["messages"]] == ["pergunta", "resposta"]


def test_invoke_aceita_mensagem_avulsa():
    builder = StateGraph(MessagesState)
    builder.add_node("eco", lambda s: {"messages": [AIMessage(content="eco")]})
    builder.add_edge(START, "eco")
    builder.add_edge("eco", END)
    out = builder.compile().invoke({"messages": HumanMessage(content="Olá!")})
    assert out["messages"][0].content == "Olá!"
    assert out["messages"][-1].content == "eco"
