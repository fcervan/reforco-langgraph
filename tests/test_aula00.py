from src.aula00_visao_geral import build_graph, versao_classica


def test_classica_e_grafo_concordam():
    assert versao_classica(True)["itens"] == ["hamburguer", "suco"]
    assert versao_classica(False)["itens"] == ["hamburguer", "agua"]
    g = build_graph()
    assert g.invoke({"itens": [], "com_sede": True})["itens"] == ["hamburguer", "suco"]
    assert g.invoke({"itens": [], "com_sede": False})["itens"] == ["hamburguer", "agua"]
