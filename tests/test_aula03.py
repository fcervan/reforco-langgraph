from langchain_core.messages import HumanMessage

from src.aula03_cadeias import build_graph, multiply


def test_multiply():
    assert multiply(3, 4) == 12


def test_cadeia_detecta_tool_offline():
    out = build_graph().invoke({"messages": [HumanMessage(content="Quanto é 3 vezes 4?")]})
    ultima = out["messages"][-1]
    assert ultima.tool_calls and ultima.tool_calls[0]["name"] == "multiply"
