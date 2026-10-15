from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.aula12_breakpoints import build_graph, fake_duas_falas


def test_pausa_antes_das_tools():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}
    chunks = list(
        graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg, stream_mode="updates")
    )
    chaves = [list(c.keys()) for c in chunks]
    assert chaves[0] == ["assistant"]
    assert chaves[-1] == ["__interrupt__"]
    assert graph.get_state(cfg).next == ("tools",)


def test_retoma_com_none_termina():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "t2"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    chunks = list(graph.stream(None, cfg, stream_mode="updates"))
    assert [list(c.keys()) for c in chunks] == [["tools"], ["assistant"]]
    final = graph.get_state(cfg)
    assert final.next == ()
    assert final.values["messages"][-1].content == "O resultado é 7."


def test_estado_mostra_pedido_pendente():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "t3"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    pedido = graph.get_state(cfg).values["messages"][-1].tool_calls[0]
    assert (pedido["name"], pedido["args"]) == ("add", {"a": 3, "b": 4})


def test_sem_checkpointer_nao_retoma():
    graph = build_graph(llm=fake_duas_falas())
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}))
    try:
        list(graph.stream(None))
        retomou = True
    except Exception:
        retomou = False
    assert not retomou  # sem sessão salva, None não tem de onde continuar


def test_interrupt_after_pausa_no_mesmo_ponto():
    from langgraph.graph import END, START, MessagesState, StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition
    from src.aula12_breakpoints import TOOLS, make_assistant

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", make_assistant(llm=fake_duas_falas()))
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    graph = builder.compile(checkpointer=MemorySaver(), interrupt_after=["assistant"])
    cfg = {"configurable": {"thread_id": "t4"}}
    list(graph.stream({"messages": [HumanMessage(content="Some 3 e 4")]}, cfg))
    assert graph.get_state(cfg).next == ("tools",)
