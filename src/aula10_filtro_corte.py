"""Aula 10 — Filtrando e cortando mensagens: conversa longa sem estourar.

Problema: o histórico cresce a cada turno; reenviá-lo inteiro ao LLM custa
tokens, latência e um dia estoura a janela. Três táticas:
1. APAGAR do estado (RemoveMessage): some de verdade, some para todos.
2. FILTRAR só no invoke (messages[-1:]): estado intacto, LLM vê recorte.
3. CORTAR por tokens (trim_messages): poda automática com orçamento.

Sem LLM nesta aula (100% offline). Execute: python src/aula10_filtro_corte.py
"""

import tiktoken
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    filter_messages,
    trim_messages,
)
from langgraph.graph import END, START, MessagesState, StateGraph

_ENC = tiktoken.get_encoding("cl100k_base")


def conta_tokens(msgs) -> int:
    """Contador didático (aproximação cl100k; produção usa o do próprio modelo)."""
    return sum(3 + len(_ENC.encode(m.content)) for m in msgs)


def conversa_exemplo() -> list:
    return [
        SystemMessage(content="Você é um atendente breve e educado da lanchonete.", id="s0"),
        HumanMessage(content="quero um pastel de carne e um suco de laranja bem gelado", id="m1"),
        AIMessage(content="Anotado: pastel e suco. Mais alguma coisa?", id="m2"),
        HumanMessage(content="adiciona um refri e me fala o total da conta por favor", id="m3"),
        AIMessage(content="Total R$ 14. Posso fechar a conta?", id="m4"),
    ]


def demo_apagar_do_estado() -> None:
    """RemoveMessage: apaga do ESTADO (vale para os próximos turnos)."""

    def filtra(state: MessagesState) -> dict:
        apaga = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        return {"messages": apaga}

    builder = StateGraph(MessagesState)
    builder.add_node("filtra", filtra)
    builder.add_edge(START, "filtra")
    builder.add_edge("filtra", END)
    out = builder.compile().invoke({"messages": conversa_exemplo()})
    print("apagar do estado (ficam as 2 últimas):")
    for m in out["messages"]:
        print(f"   [{type(m).__name__} {m.id}] {m.content!r}")


def demo_filtrar_so_no_invoke() -> None:
    """Recorte só na chamada: o estado continua completo."""

    def eco(state: MessagesState) -> dict:
        vista = state["messages"][-1:]
        return {"messages": [AIMessage(content=f"vi {len(vista)} msg(s): {vista[0].content}")]}

    builder = StateGraph(MessagesState)
    builder.add_node("eco", eco)
    builder.add_edge(START, "eco")
    builder.add_edge("eco", END)
    out = builder.compile().invoke({"messages": conversa_exemplo()})
    print(f"filtrar no invoke: estado tem {len(out['messages'])} msgs,")
    print(f"   mas o nó viu 1 -> {out['messages'][-1].content!r}")


def demo_trim() -> None:
    """trim_messages: poda automática por orçamento de tokens."""
    msgs = conversa_exemplo()
    print(f"conversa completa: {conta_tokens(msgs)} tokens")
    cortada = trim_messages(
        msgs, max_tokens=40, strategy="last", token_counter=conta_tokens,
        include_system=True, allow_partial=False,
    )
    print("trim 40 + system:", [(type(m).__name__, m.id) for m in cortada],
          f"-> {conta_tokens(cortada)} tokens")


def demo_start_on_e_sem_system() -> None:
    """start_on='human' exige começar em fala humana; sem system o SYS cai."""
    msgs = conversa_exemplo()
    so_humano = trim_messages(
        msgs, max_tokens=40, strategy="last", token_counter=conta_tokens,
        include_system=True, start_on="human", allow_partial=False,
    )
    print("start_on=human:", [(type(m).__name__, m.id) for m in so_humano])
    sem_sys = trim_messages(
        msgs, max_tokens=40, strategy="last", token_counter=conta_tokens,
        include_system=False, allow_partial=False,
    )
    print("sem system:", [(type(m).__name__, m.id) for m in sem_sys])


def demo_partial() -> None:
    """allow_partial=True aproveita o fim da mensagem longa (por linhas)."""
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
    print("partial=False:", [(m.id, m.content) for m in inteira])
    print("partial=True :", [(m.id, m.content) for m in parcial])


def demo_filter_messages() -> None:
    """filter_messages: recorte por tipo/remetente, sem grafo."""
    msgs = conversa_exemplo()
    print("só humanas:", [m.content for m in filter_messages(msgs, include_types=["human"])])


def main() -> None:
    print("=== 1. apagar do estado (RemoveMessage) ===")
    demo_apagar_do_estado()
    print("\n=== 2. filtrar só no invoke (estado intacto) ===")
    demo_filtrar_so_no_invoke()
    print("\n=== 3. cortar por tokens (trim_messages) ===")
    demo_trim()
    print("\n=== 4. start_on e system ===")
    demo_start_on_e_sem_system()
    print("\n=== 5. mensagem parcial ===")
    demo_partial()
    print("\n=== 6. filter_messages por tipo ===")
    demo_filter_messages()


if __name__ == "__main__":
    main()
