"""Aula 14 — Breakpoints dinâmicos: pausar por REGRA, não por lista.

Na Aula 12 o fiscal parava TUDO (`interrupt_before=["tools"]`). Aqui ele só
para o que a regra manda:
- API do curso: `raise NodeInterrupt("motivo")` dentro do nó (condicional).
  Depreciada na v1.0 — funciona, mas avisa.
- API nova: `valor = interrupt("motivo")` pausa; na retomada com
  `Command(resume=resposta)`, o retorno é a resposta do humano.

Sem LLM nesta aula (100% offline). Execute: python src/aula14_dinamico.py
"""

import warnings
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

warnings.filterwarnings("ignore")  # cala deprecations nas demos (a aula mostra elas)

LIMITE = 50.0


class Conta(TypedDict):
    entrada: str
    total: float


def build_estatico():
    """Aula 12: pausa sempre (lista fixa)."""
    builder = StateGraph(Conta)
    builder.add_node("caixa", lambda s: {"total": s["total"]})
    builder.add_edge(START, "caixa")
    builder.add_edge("caixa", END)
    return builder.compile(checkpointer=MemorySaver(), interrupt_before=["caixa"])


def build_dinamico():
    """Pausa SÓ se a regra mandar (conta acima do limite)."""

    def caixa(state: Conta) -> dict:
        if state["total"] > LIMITE:
            raise NodeInterrupt(f"conta R$ {state['total']} acima de R$ {LIMITE}")
        return {"total": state["total"]}

    builder = StateGraph(Conta)
    builder.add_node("caixa", caixa)
    builder.add_edge(START, "caixa")
    builder.add_edge("caixa", END)
    return builder.compile(checkpointer=MemorySaver())


def conta_baixa_passa_direto() -> None:
    out = build_dinamico().invoke(
        {"entrada": "pastel", "total": 14.0}, {"configurable": {"thread_id": "b1"}}
    )
    print("conta baixa:", out, "(sem pausa: a regra não mandou)")


def conta_alta_pausa() -> None:
    graph = build_dinamico()
    cfg = {"configurable": {"thread_id": "b2"}}
    for chunk in graph.stream(
        {"entrada": "banquete", "total": 55.0}, cfg, stream_mode="updates"
    ):
        print("  ", list(chunk.keys()))
    estado = graph.get_state(cfg)
    print("next:", estado.next)
    for tarefa in estado.tasks:
        for pausa in tarefa.interrupts:
            print(f"motivo em {tarefa.name}: {pausa.value}")


def retomar_sem_mudar_trava() -> None:
    """Sem mudar o estado, retomar executa o MESMO nó -> pausa DE NOVO."""
    graph = build_dinamico()
    cfg = {"configurable": {"thread_id": "b3"}}
    list(graph.stream({"entrada": "banquete", "total": 55.0}, cfg))
    list(graph.stream(None, cfg))
    print("next após retomar sem mudar:", graph.get_state(cfg).next)
    print("-> preso: a regra manda pausar de novo. Saída: update_state (Aula 13).")


def update_destrava() -> None:
    graph = build_dinamico()
    cfg = {"configurable": {"thread_id": "b4"}}
    list(graph.stream({"entrada": "banquete", "total": 55.0}, cfg))
    graph.update_state(cfg, {"total": 40.0})  # fiscal concede desconto
    print("após desconto:", graph.invoke(None, cfg))


def demo_api_nova() -> None:
    """interrupt() devolve a resposta do humano na retomada (Command)."""

    class ContaAprovada(TypedDict):
        entrada: str
        total: float
        aprovado: bool

    def caixa(state: ContaAprovada) -> dict:
        if state["total"] > LIMITE and not state.get("aprovado"):
            decisao = interrupt(f"conta R$ {state['total']} acima do limite: aprova?")
            if decisao is True:
                return {"aprovado": True}
        return {"total": state["total"]}

    builder = StateGraph(ContaAprovada)
    builder.add_node("caixa", caixa)
    builder.add_edge(START, "caixa")
    builder.add_edge("caixa", END)
    graph = builder.compile(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "nova"}}
    list(graph.stream({"entrada": "banquete", "total": 55.0}, cfg))
    print("pausado. retomando com Command(resume=True)...")
    list(graph.stream(Command(resume=True), cfg))
    print("final:", graph.get_state(cfg).values)


def main() -> None:
    print("=== 1. conta baixa passa direto ===")
    conta_baixa_passa_direto()
    print("\n=== 2. conta alta pausa (com motivo) ===")
    conta_alta_pausa()
    print("\n=== 3. retomar sem mudar trava ===")
    retomar_sem_mudar_trava()
    print("\n=== 4. update_state destrava ===")
    update_destrava()
    print("\n=== 5. API nova: interrupt + Command ===")
    demo_api_nova()


if __name__ == "__main__":
    main()
