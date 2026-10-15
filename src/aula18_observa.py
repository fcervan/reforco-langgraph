"""Aula 18 — Observabilidade: enxergar pai e filhos sem LangSmith.

O LangSmith é o mesmo protocolo de callbacks, só que na nuvem (exige
LANGCHAIN_API_KEY, que não temos aqui). A aula constrói o equivalente local:
um handler que monta a árvore pai -> filhos com tempo e erros por nó.

Execute: python src/aula18_observa.py (100% offline)
"""

import time

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph


class RastreadorLocal(BaseCallbackHandler):
    """Monta a árvore de execução: nome, tempo e status por nó."""

    def __init__(self):
        self.linhas = []
        self._inicio = {}
        self._nomes = {}
        self._prof = {}

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None,
                       name=None, **kwargs):
        self._nomes[run_id] = name
        self._inicio[run_id] = time.perf_counter()
        self._prof[run_id] = self._prof.get(parent_run_id, -1) + 1

    def _fecha(self, run_id, status: str):
        dt = (time.perf_counter() - self._inicio.pop(run_id)) * 1000
        rec = "  " * self._prof.get(run_id, 0) + str(self._nomes.get(run_id))
        self.linhas.append((rec, f"{dt:.1f}ms", status))

    def on_chain_end(self, outputs, *, run_id, **kwargs):
        self._fecha(run_id, "ok")

    def on_chain_error(self, error, *, run_id, **kwargs):
        self._fecha(run_id, f"ERRO {type(error).__name__}")


def sub_grafinho(nome_no: str, quebra: bool = False):
    builder = StateGraph(MessagesState)

    def ruim(state: MessagesState) -> dict:
        raise RuntimeError("pane no filho")

    builder.add_node(nome_no, ruim if quebra else (lambda s: {"messages": []}))
    builder.add_edge(START, nome_no)
    builder.add_edge(nome_no, END)
    return builder.compile()


def build_pai(com_erro: bool = False):
    builder = StateGraph(MessagesState)
    builder.add_node("filho_ok", sub_grafinho("trabalha_ok"))
    builder.add_node("filho_outro", sub_grafinho("trabalha_outro", quebra=com_erro))
    builder.add_edge(START, "filho_ok")
    builder.add_edge(START, "filho_outro")
    builder.add_edge("filho_ok", END)
    builder.add_edge("filho_outro", END)
    return builder.compile()


def demo_arvore() -> RastreadorLocal:
    """Pai + 2 filhos ok: árvore com tempos."""
    rast = RastreadorLocal()
    list(
        build_pai().stream(
            {"messages": [HumanMessage(content="oi")]}, config={"callbacks": [rast]}
        )
    )
    for nome, tempo, status in rast.linhas:
        print(f"{nome} [{tempo}] {status}")
    return rast


def demo_erro() -> RastreadorLocal:
    """Filho que explode: o caminho do erro sobe até o pai."""
    rast = RastreadorLocal()
    try:
        list(
            build_pai(com_erro=True).stream(
                {"messages": [HumanMessage(content="oi")]}, config={"callbacks": [rast]}
            )
        )
    except RuntimeError as erro:
        print(f"(propagou: {erro})")
    for nome, tempo, status in rast.linhas:
        print(f"{nome} [{tempo}] {status}")
    return rast


def demo_langsmith_opcional() -> None:
    """Com LANGCHAIN_API_KEY, o MESMO código traça na nuvem com 3 linhas."""
    import os

    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ.setdefault("LANGCHAIN_PROJECT", "reforco-langgraph")
        print("tracing ativo: veja em https://smith.langchain.com (projeto reforco-langgraph)")
    else:
        print("sem LANGCHAIN_API_KEY: o RastreadorLocal acima é o equivalente.")
        print("quando tiver a chave, exporte estas 3 e rode o mesmo código:")
        print("  LANGCHAIN_TRACING_V2=true")
        print("  LANGCHAIN_API_KEY=<sua>")
        print("  LANGCHAIN_PROJECT=reforco-langgraph  (opcional)")


def main() -> None:
    print("=== 1. árvore pai -> filhos (tempos) ===")
    demo_arvore()
    print("\n=== 2. caminho do erro ===")
    demo_erro()
    print("\n=== 3. LangSmith (opcional, sem chave aqui) ===")
    demo_langsmith_opcional()


if __name__ == "__main__":
    main()
