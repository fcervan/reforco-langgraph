from src.aula18_observa import RastreadorLocal, build_pai, demo_arvore, demo_erro
from langchain_core.messages import HumanMessage


def test_arvore_tem_pai_e_filhos_com_tempo():
    rast = demo_arvore()
    nomes = [n.strip() for n, _, _ in rast.linhas]
    assert any("filho_ok" in n for n in nomes)
    assert any("filho_outro" in n for n in nomes)
    assert any("trabalha_ok" in n for n in nomes)
    assert all(t.endswith("ms") for _, t, _ in rast.linhas)
    assert all(s == "ok" for _, _, s in rast.linhas)


def test_filhos_indentados_sob_o_pai():
    rast = demo_arvore()
    nomes = [n for n, _, _ in rast.linhas]
    raizes = [n for n in nomes if not n.startswith(" ")]
    assert raizes and raizes[-1].strip() == "LangGraph"  # raiz fecha por último
    assert any(n.startswith("    ") for n in nomes)  # há netos (nós dos filhos)


def test_erro_sobe_ate_o_pai():
    rast = demo_erro()
    erros = [(n.strip(), s) for n, _, s in rast.linhas if s.startswith("ERRO")]
    assert erros, "nenhum erro registrado"
    assert any("trabalha_outro" in n for n, _ in erros)
    assert erros[-1][0] == "LangGraph"  # o último a fechar com erro é o pai


def test_sem_filhos_quebrados_nada_falha():
    rast = RastreadorLocal()
    list(
        build_pai().stream(
            {"messages": [HumanMessage(content="oi")]}, config={"callbacks": [rast]}
        )
    )
    assert rast.linhas and all(s == "ok" for _, _, s in rast.linhas)
