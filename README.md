# Reforço LangGraph — do zero até Schemas Múltiplos

Estudo aula a aula para dev clássico/determinístico entender LangGraph
de verdade: cada notebook tem analogia com `função + dict + if/else`,
código dissecado linha a linha, variações que quebram, erros comuns
e desafio. Sem matemática de LLM.

Padrão: Groq como LLM primário (`GROQ_API_KEY` via `.env`, nunca versionado),
modelo padrão `openai/gpt-oss-20b`.
Sem chave, tudo roda **offline** com Fake determinístico.

## Status (novo padrão didático, 1 notebook por entrega)

- [x] 00 Visão Geral — lanchonete clássica vs grafo, tabela de tradução, chain vs graph
- [x] 01 Setup — `uv` vs pip, `.env`+`getpass`, Groq, `invoke vs stream`, `AIMessage`
- [ ] 01 Setup/Instalação — venv, `.env`+`getpass`, Groq, `invoke vs stream`, `Human/AIMessage`
- [ ] 02 Grafos — `TypedDict`, nó, aresta, condicional, `compile/invoke`, overwrite
- [ ] 03 Cadeias — `messages`, `bind_tools` (detecta, não executa), `add_messages`
- [ ] 04 Roteadores — `ToolNode` + `tools_condition`
- [ ] 05 Agente ReAct, 06 Memória, 07 Schemas, 08 Reducers, 09 Schemas Múltiplos

Mapeia `Curso_Introdutorio_de_Langgraph/module-1` e `modulo-2`.

> Nota de limpeza: os notebooks mínimos 02–04 da primeira tentativa foram
> removidos (confundiam). Os `src/aula02-04.py` foram mantidos como espelhos
> executáveis e serão expandidos quando as aulas forem refeitas no novo padrão.

## Uso rápido

```bash
pip install -r requirements.txt
# ou com uv (recomendado): uv venv && uv sync
python src/aula00_visao_geral.py   # sem LLM, 100% offline
python src/aula01_setup.py         # Groq real com GROQ_API_KEY, senão Fake
python -m pytest tests/ -q         # 11 testes offline (+1 só com chave real)
jupyter notebook notebooks/00_visao_geral.ipynb
```

Com Groq real (opcional, a partir da Aula 01):

```bash
cp .env.example .env  # preencher GROQ_API_KEY
```

## Estrutura

```
src/aula00_visao_geral.py   # lanchonete clássica + mesmo fluxo em StateGraph
src/aula01_setup.py         # get_llm() Groq-ou-Fake + demo invoke/stream
notebooks/00_visao_geral.ipynb  # 11 células: analogia, 3 codes, dissecção, erros, desafio
notebooks/01_setup.ipynb        # 14 células: uv vs pip, chave, temperature, stream, desafio
src/aula02_grafo.py, aula03_cadeias.py, aula04_roteador.py  # espelhos (serão expandidos)
tests/test_aula00.py ...    # offline, determinístico
```

## O que a Aula 00 ensina

| Conceito | Tradução dev clássico |
|---|---|
| Estado | dict compartilhado (`TypedDict` = contrato) |
| Nó | função `f(state)->update parcial` |
| Aresta | ordem fixa `A -> B` |
| Aresta condicional | seu `if`, retorna nome do próximo nó |
| `compile/invoke` | montar fluxograma / rodar do `START` ao `END` |
| Chain vs Graph | cano reto vs fluxograma com ciclo/decisão runtime |
