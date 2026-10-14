import os

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.errors import GraphRecursionError

from src.aula05_agente import TOOLS, add, build_graph, divide, get_llm, multiply


def fake_sequencia():
    return FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 3, "b": 4}, "id": "c1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="O resultado é 7.", tool_calls=[]),
        ]
    )


def test_loop_completa_pedido_recibo_resposta():
    graph = build_graph(llm=fake_sequencia(), loop_back=True)
    out = graph.invoke({"messages": [HumanMessage(content="Some 3 e 4")]})
    tipos = [type(m).__name__ for m in out["messages"]]
    assert tipos == ["HumanMessage", "AIMessage", "ToolMessage", "AIMessage"]
    assert out["messages"][2].content == "7"  # o recibo
    assert "7" in out["messages"][3].content  # o LLM releu o recibo


def test_sem_volta_termina_no_recibo():
    graph = build_graph(llm=fake_sequencia(), loop_back=False)
    out = graph.invoke({"messages": [HumanMessage(content="Some 3 e 4")]})
    tipos = [type(m).__name__ for m in out["messages"]]
    assert tipos == ["HumanMessage", "AIMessage", "ToolMessage"]


def test_limite_recursao_protege_loop_infinito():
    teimoso = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "add", "args": {"a": 1, "b": 1}, "id": "c9", "type": "tool_call"}
                ],
            )
        ]
    )
    graph = build_graph(llm=teimoso, loop_back=True)
    with pytest.raises(GraphRecursionError):
        graph.invoke(
            {"messages": [HumanMessage(content="Some 1 e 1")]},
            config={"recursion_limit": 3},
        )


def test_tools_basicas():
    assert add(3, 4) == 7
    assert multiply(3, 4) == 12
    assert divide(20, 4) == 5
    assert [t.__name__ if hasattr(t, "__name__") else t.name for t in TOOLS] == [
        "add",
        "multiply",
        "divide",
    ]


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="só com chave real")
def test_groq_real_encadeia_tres_contas():
    graph = build_graph(loop_back=True)
    out = graph.invoke(
        {"messages": [HumanMessage(content="Some 3 e 4, depois multiplique por 2, "
                                            "e finalmente divida por 5. Mostre o resultado.")]}
    )
    final = out["messages"][-1].content
    assert "2,8" in final or "2.8" in final, final
    tipos = [type(m).__name__ for m in out["messages"]]
    assert tipos.count("ToolMessage") >= 2  # pelo menos 2 execuções reais
    assert tipos[-1] == "AIMessage" and not out["messages"][-1].tool_calls
