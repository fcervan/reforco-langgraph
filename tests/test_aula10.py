from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    filter_messages,
    trim_messages,
)
from langgraph.graph import END, START, MessagesState, StateGraph

from src.aula10_filtro_corte import conta_tokens, conversa_exemplo


def test_apagar_do_estado_mantem_2_ultimas():
    from langchain_core.messages import RemoveMessage

    def filtra(state: MessagesState) -> dict:
        return {"messages": [RemoveMessage(id=m.id) for m in state["messages"][:-2]]}

    builder = StateGraph(MessagesState)
    builder.add_node("filtra", filtra)
    builder.add_edge(START, "filtra")
    builder.add_edge("filtra", END)
    out = builder.compile().invoke({"messages": conversa_exemplo()})
    assert [m.id for m in out["messages"]] == ["m3", "m4"]


def test_filtrar_so_no_invoke_mantem_estado():
    def eco(state: MessagesState) -> dict:
        vista = state["messages"][-1:]
        return {"messages": [AIMessage(content=f"vi {len(vista)}")]}

    builder = StateGraph(MessagesState)
    builder.add_node("eco", eco)
    builder.add_edge(START, "eco")
    builder.add_edge("eco", END)
    out = builder.compile().invoke({"messages": conversa_exemplo()})
    assert len(out["messages"]) == 6  # 5 originais + 1 resposta
    assert out["messages"][-1].content == "vi 1"


def test_trim_cabe_no_orcamento():
    cortada = trim_messages(
        conversa_exemplo(), max_tokens=40, strategy="last",
        token_counter=conta_tokens, include_system=True, allow_partial=False,
    )
    assert conta_tokens(cortada) <= 40
    assert cortada[0].id == "s0"  # system preservado
    assert cortada[-1].id == "m4"  # fim preservado


def test_trim_sem_system_cai_o_sys():
    cortada = trim_messages(
        conversa_exemplo(), max_tokens=40, strategy="last",
        token_counter=conta_tokens, include_system=False, allow_partial=False,
    )
    assert all(type(m).__name__ != "SystemMessage" for m in cortada)
    assert [m.id for m in cortada] == ["m3", "m4"]


def test_partial_aproveita_fim_da_longa():
    msgs = [
        HumanMessage(
            content="linha um do pedido\nlinha dois do pedido\nlinha três do pedido\nlinha quatro do pedido",
            id="m1",
        ),
        AIMessage(content="Anotado.", id="m2"),
        HumanMessage(content="adiciona um refri", id="m3"),
    ]
    inteira = trim_messages(
        msgs, max_tokens=30, strategy="last", token_counter=conta_tokens,
        include_system=False, allow_partial=False,
    )
    parcial = trim_messages(
        msgs, max_tokens=30, strategy="last", token_counter=conta_tokens,
        include_system=False, allow_partial=True,
    )
    assert [m.id for m in inteira] == ["m2", "m3"]  # m1 caiu inteira
    assert parcial[0].id == "m1" and "quatro" in parcial[0].content  # fim aproveitado


def test_filter_messages_por_tipo():
    humanas = filter_messages(conversa_exemplo(), include_types=["human"])
    assert [m.content for m in humanas] == [
        "quero um pastel de carne e um suco de laranja bem gelado",
        "adiciona um refri e me fala o total da conta por favor",
    ]
    assert all(type(m).__name__ == "HumanMessage" for m in humanas)


def test_contador_e_conversa_sao_consistentes():
    msgs = conversa_exemplo()
    assert len(msgs) == 5
    assert conta_tokens(msgs) > 40  # sem folga: o trim realmente corta
    assert isinstance(msgs[0], SystemMessage)
