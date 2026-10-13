# Reforço LangGraph — do zero até Schemas Múltiplos

Estudo aula a aula para dev clássico/determinístico entender LangGraph
de verdade: cada notebook tem analogia com `função + dict + if/else`,
código dissecado linha a linha, variações que quebram, erros comuns
e desafio. Sem matemática de LLM.

Padrão: Groq como LLM primário (`GROQ_API_KEY` via `.env`, nunca versionado),
modelo padrão `openai/gpt-oss-20b`, **sempre com `reasoning_effort="low"`**
(modelo de raciocínio: sem isso ele gasta todo o orçamento de tokens pensando,
estoura em `finish_reason: length` e devolve `content` vazio — ver seção 3.1
da Aula 01).
Sem chave, tudo roda **offline** com Fake determinístico.

## Status (novo padrão didático, 1 notebook por entrega)

- [x] 00 Visão Geral — lanchonete clássica vs grafo, tabela de tradução, chain vs graph
- [x] 01 Setup — `uv` vs pip, `.env`+`getpass`, Groq, `invoke vs stream`, `AIMessage`
- [x] 01.1 (fix) — `reasoning_effort="low"`: modelo de raciocínio e o `content` vazio
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
python -m pytest tests/ -q         # testes offline (+1 só com chave real)
jupyter notebook notebooks/00_visao_geral.ipynb
```

Com Groq real (a partir da Aula 01):

```bash
cp .env.example .env  # preencher GROQ_API_KEY
```

## No Colab

O notebook `01_setup.ipynb` é autocontido (a aula 00 também) e vem com uma
**célula 0 de instalação** — ela roda `%pip install -q langgraph langchain-groq
python-dotenv`, porque o Colab começa sem esses pacotes. Localmente, se você
já fez `uv sync`, a célula é inofensivo (no-op).

```python
# dentro do Colab, uma vez por sessão
!git clone https://github.com/fcervan/reforco-langgraph.git
%cd reforco-langgraph
!git pull                      # antes de cada vez que abrir
%pip install -q -r requirements.txt
# e cole a chave quando a célula 2 pedir (digitação oculta)
```

Por que `get_llm` cai no Fake se o pacote faltar: sem isso, adicionar a chave
num Colab recém-criado estourava `ModuleNotFoundError` no meio da aula. Agora
ele avisa o comando de instalação e continua em modo offline.

## Estrutura

```
src/aula00_visao_geral.py   # lanchonete clássica + mesmo fluxo em StateGraph
src/aula01_setup.py         # get_llm() Groq-ou-Fake (tolera falta do pacote) + invoke/stream
notebooks/00_visao_geral.ipynb  # 11 células: analogia, 3 codes, dissecção, erros, desafio
notebooks/01_setup.ipynb        # 15 células: celula pip, uv vs pip, chave, temperature, stream
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
