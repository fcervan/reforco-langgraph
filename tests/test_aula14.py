from src.aula14_dinamico import build_dinamico, build_estatico


def _cfg(tid: str) -> dict:
    return {"configurable": {"thread_id": tid}}


def test_estatico_pausa_sempre():
    graph = build_estatico()
    list(graph.stream({"entrada": "x", "total": 1.0}, _cfg("e1")))
    assert graph.get_state(_cfg("e1")).next == ("caixa",)


def test_dinamico_conta_baixa_passa_direto():
    out = build_dinamico().invoke({"entrada": "pastel", "total": 14.0}, _cfg("e2"))
    assert out == {"entrada": "pastel", "total": 14.0}


def test_dinamico_conta_alta_pausa_com_motivo():
    graph = build_dinamico()
    chunks = list(graph.stream({"entrada": "banquete", "total": 55.0}, _cfg("e3")))
    assert [list(c.keys()) for c in chunks] == [["__interrupt__"]]
    estado = graph.get_state(_cfg("e3"))
    assert estado.next == ("caixa",)
    motivos = [p.value for t in estado.tasks for p in t.interrupts]
    assert any("55.0" in str(m) for m in motivos)


def test_retomar_sem_mudar_pausa_de_novo():
    graph = build_dinamico()
    list(graph.stream({"entrada": "banquete", "total": 55.0}, _cfg("e4")))
    list(graph.stream(None, _cfg("e4")))
    assert graph.get_state(_cfg("e4")).next == ("caixa",)


def test_update_destrava():
    graph = build_dinamico()
    list(graph.stream({"entrada": "banquete", "total": 55.0}, _cfg("e5")))
    graph.update_state(_cfg("e5"), {"total": 40.0})
    assert graph.invoke(None, _cfg("e5")) == {"entrada": "banquete", "total": 40.0}


def test_api_nova_aprova_com_command():
    import warnings

    from langgraph.graph import END, START, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command, interrupt
    from typing import TypedDict

    warnings.filterwarnings("ignore")

    class ContaAprovada(TypedDict):
        entrada: str
        total: float
        aprovado: bool

    def caixa(state: ContaAprovada) -> dict:
        if state["total"] > 50.0 and not state.get("aprovado"):
            if interrupt("aprova?") is True:
                return {"aprovado": True}
        return {"total": state["total"]}

    builder = StateGraph(ContaAprovada)
    builder.add_node("caixa", caixa)
    builder.add_edge(START, "caixa")
    builder.add_edge("caixa", END)
    graph = builder.compile(checkpointer=MemorySaver())
    cfg = _cfg("e6")
    list(graph.stream({"entrada": "banquete", "total": 55.0}, cfg))
    assert graph.get_state(cfg).next == ("caixa",)
    list(graph.stream(Command(resume=True), cfg))
    assert graph.get_state(cfg).values["aprovado"] is True
