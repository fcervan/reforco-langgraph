from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.aula13_feedback import TOOLS, build_base, fake_pedido_soma, make_assistant


def test_corrige_pedido_executa_o_novo():
    graph, cfg = _pausado("t1")
    pedido = graph.get_state(cfg).values["messages"][-1]
    assert (pedido.tool_calls[0]["name"], pedido.tool_calls[0]["args"]) == ("add", {"a": 3, "b": 4})
    corrigido = AIMessage(
        content="",
        id=pedido.id,
        tool_calls=[
            {"name": "multiply", "args": {"a": 3, "b": 10}, "id": "c1", "type": "tool_call"}
        ],
    )
    graph.update_state(cfg, {"messages": [corrigido]})
    list(graph.stream(None, cfg))
    recibos = [
        m.content
        for m in graph.get_state(cfg).values["messages"]
        if type(m).__name__ == "ToolMessage"
    ]
    assert recibos == ["30"]  # executou o corrigido, não o original


def test_anexar_sem_id_soma():
    graph, cfg = _pausado("t2")
    antes = len(graph.get_state(cfg).values["messages"])
    graph.update_state(cfg, {"messages": [HumanMessage(content="urgente")]})
    depois = len(graph.get_state(cfg).values["messages"])
    assert depois == antes + 1


def test_feedback_assinado_precisa_do_no():
    graph, cfg = _pausado("t3")
    try:
        graph.update_state(cfg, {"messages": [HumanMessage(content="oi")]}, as_node="fantasma")
        assinou = True
    except Exception:
        assinou = False
    assert not assinou


def test_placeholder_permite_as_node():
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm=fake_pedido_soma()))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("feedback_humano", lambda state: {})
    builder.add_edge(START, "feedback_humano")
    builder.add_edge("feedback_humano", "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    graph = builder.compile(checkpointer=MemorySaver(), interrupt_before=["feedback_humano"])
    cfg = {"configurable": {"thread_id": "t4"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    assert graph.get_state(cfg).next == ("feedback_humano",)
    graph.update_state(
        cfg, {"messages": [HumanMessage(content="dobra isso")]}, as_node="feedback_humano"
    )
    list(graph.stream(None, cfg))
    msgs = graph.get_state(cfg).values["messages"]
    assert msgs[1].content == "dobra isso"


def _pausado(thread: str):
    graph = build_base(llm=fake_pedido_soma())
    cfg = {"configurable": {"thread_id": thread}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    assert graph.get_state(cfg).next == ("tools",)
    return graph, cfg
