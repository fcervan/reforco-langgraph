from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.aula04_roteador import build_graph


def test_conta_vai_para_tools():
    out = build_graph(conta=True).invoke({"messages": [HumanMessage(content="Quanto é 3x4?")]})
    tipos = [type(m).__name__ for m in out["messages"]]
    assert tipos == ["HumanMessage", "AIMessage", "ToolMessage"]
    assert isinstance(out["messages"][-1], ToolMessage)
    assert out["messages"][-1].content == "12"


def test_conversa_simples_encerra_sem_tool():
    out = build_graph(conta=False).invoke({"messages": [HumanMessage(content="Oi")]})
    ultima = out["messages"][-1]
    assert isinstance(ultima, AIMessage) and not ultima.tool_calls
