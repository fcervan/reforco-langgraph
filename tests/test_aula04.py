import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.aula04_roteador import TOOLS, build_graph, divide, multiply, soma


def test_conta_vai_para_tools():
    out = build_graph(conta=True).invoke({"messages": [HumanMessage(content="Quanto é 3x4?")]})
    tipos = [type(m).__name__ for m in out["messages"]]
    assert tipos == ["HumanMessage", "AIMessage", "ToolMessage"]
    ultima = out["messages"][-1]
    assert isinstance(ultima, ToolMessage)
    assert ultima.content == "12"
    assert ultima.name == "multiply"


def test_toolmessage_carrega_id_do_pedido():
    out = build_graph(conta=True).invoke({"messages": [HumanMessage(content="Quanto é 3x4?")]})
    pedido = out["messages"][1]
    resposta = out["messages"][2]
    assert pedido.tool_calls[0]["id"] == resposta.tool_call_id


def test_conversa_simples_encerra_sem_tool():
    out = build_graph(conta=False).invoke({"messages": [HumanMessage(content="Oi")]})
    ultima = out["messages"][-1]
    assert isinstance(ultima, AIMessage) and not ultima.tool_calls
    assert [type(m).__name__ for m in out["messages"]] == ["HumanMessage", "AIMessage"]


def test_tools_condition_devolve_rota_correta():
    com_pedido = {
        "messages": [
            HumanMessage(content="x"),
            AIMessage(
                content="",
                tool_calls=[{"name": "multiply", "args": {"a": 1, "b": 2}, "id": "c1", "type": "tool_call"}],
            ),
        ]
    }
    assert tools_condition(com_pedido) == "tools"
    sem_pedido = {"messages": [HumanMessage(content="x"), AIMessage(content="oi")]}
    assert tools_condition(sem_pedido) == END


def test_tool_fora_da_lista_vira_mensagem_de_erro():
    """Pedir tool desconhecida NÃO quebra: vira ToolMessage de erro."""
    pedido = AIMessage(
        content="",
        tool_calls=[{"name": "fantasma", "args": {}, "id": "c1", "type": "tool_call"}],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    out = builder.compile().invoke({"messages": [pedido]})
    assert "not a valid tool" in out["messages"][-1].content


def test_erro_na_tool_propaga():
    """Exceção DENTRO da tool quebra a execução (não vira ToolMessage)."""
    pedido = AIMessage(
        content="",
        tool_calls=[{"name": "divide", "args": {"a": 1, "b": 0}, "id": "c2", "type": "tool_call"}],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode([divide]))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    with pytest.raises(ZeroDivisionError):
        builder.compile().invoke({"messages": [pedido]})


def test_dois_pedidos_dois_resultados():
    pedido = AIMessage(
        content="",
        tool_calls=[
            {"name": "multiply", "args": {"a": 2, "b": 3}, "id": "c3", "type": "tool_call"},
            {"name": "multiply", "args": {"a": 4, "b": 5}, "id": "c4", "type": "tool_call"},
        ],
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    out = builder.compile().invoke({"messages": [pedido]})
    resultados = [(m.content, m.tool_call_id) for m in out["messages"][1:]]
    assert resultados == [("6", "c3"), ("20", "c4")]


def test_tools_basicas():
    assert multiply(3, 4) == 12
    assert soma(10, 5) == 15
    assert divide(20, 4) == 5
