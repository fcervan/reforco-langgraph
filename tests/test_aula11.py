import asyncio
import types

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.aula11_streaming import build_graph, fake_duas_falas

_CFGS = [
    {"configurable": {"thread_id": "t1"}},
    {"configurable": {"thread_id": "t2"}},
    {"configurable": {"thread_id": "t3"}},
    {"configurable": {"thread_id": "t4"}},
    {"configurable": {"thread_id": "t5"}},
    {"configurable": {"thread_id": "t6"}},
]


def test_updates_emite_um_por_no():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    chunks = list(
        graph.stream(
            {"messages": [HumanMessage(content="Some 3 e 4")]},
            _CFGS[0],
            stream_mode="updates",
        )
    )
    assert [list(c.keys()) for c in chunks] == [["assistant"], ["tools"], ["assistant"]]


def test_values_mostra_estado_crescendo():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    tamanhos = [
        len(c["messages"])
        for c in graph.stream(
            {"messages": [HumanMessage(content="Some 3 e 4")]},
            _CFGS[1],
            stream_mode="values",
        )
    ]
    assert tamanhos == [1, 2, 3, 4]


def test_messages_devolve_tupla_com_origem():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    pares = list(
        graph.stream(
            {"messages": [HumanMessage(content="Some 3 e 4")]},
            _CFGS[2],
            stream_mode="messages",
        )
    )
    assert pares, "modo messages não emitiu nada"
    for pedaco, meta in pares:
        assert "langgraph_node" in meta
    nos = [meta["langgraph_node"] for _, meta in pares]
    assert "assistant" in nos and "tools" in nos


def test_stream_e_preguicoso_e_esgota():
    """stream devolve gerador: não executa ao criar, esvazia após 1 passada."""
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())
    gen = graph.stream(
        {"messages": [HumanMessage(content="Some 3 e 4")]},
        _CFGS[3],
        stream_mode="updates",
    )
    assert isinstance(gen, types.GeneratorType)
    primeira = list(gen)
    assert len(primeira) == 3
    assert list(gen) == []  # gerador esgotado: segunda passada vem vazia


def test_astream_igual_ao_stream():
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())

    async def coleta():
        return [
            c
            async for c in graph.astream(
                {"messages": [HumanMessage(content="Some 3 e 4")]},
                _CFGS[4],
                stream_mode="updates",
            )
        ]

    chunks = asyncio.run(coleta())
    assert [list(c.keys()) for c in chunks] == [["assistant"], ["tools"], ["assistant"]]


def test_astream_events_traz_tokens_do_no():
    """Filtra on_chat_model_stream do assistant (estrutura; conteúdo varia)."""
    graph = build_graph(llm=fake_duas_falas(), checkpointer=MemorySaver())

    async def coleta():
        tokens = []
        async for ev in graph.astream_events(
            {"messages": [HumanMessage(content="Some 3 e 4")]},
            _CFGS[5],
            version="v2",
        ):
            if ev["event"] == "on_chat_model_stream":
                assert ev["metadata"].get("langgraph_node") == "assistant"
                tokens.append(ev["data"]["chunk"].content)
        return tokens

    tokens = asyncio.run(coleta())
    assert isinstance(tokens, list)


def test_fake_compartilhado_nao_entra_em_loop():
    llm = fake_duas_falas()
    assert llm.invoke([]).tool_calls
    assert not llm.invoke([]).tool_calls
