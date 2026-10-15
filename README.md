# Reforço LangGraph — do zero até Schemas Múltiplos

[![Abrir 00 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/00_visao_geral.ipynb) [![Abrir 01 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/01_setup.ipynb) [![Abrir 02 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/02_grafos.ipynb) [![Abrir 03 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/03_cadeias.ipynb) [![Abrir 04 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/04_roteadores.ipynb) [![Abrir 05 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/05_agente_react.ipynb) [![Abrir 06 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/06_memoria.ipynb) [![Abrir 07 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/07_schemas.ipynb) [![Abrir 08 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/08_reducers.ipynb) [![Abrir 09 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/09_schemas_multiplos.ipynb) [![Abrir 10 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/10_filtro_corte.ipynb) [![Abrir 11 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/11_streaming_hitl.ipynb) [![Abrir 12 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/12_breakpoints.ipynb) [![Abrir 13 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/13_feedback_humano.ipynb)

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
- [x] 02 Grafos — `TypedDict`, nó, aresta, condicional, `compile/invoke`, overwrite,
      visualização (`draw_mermaid`/`draw_ascii`) e 6 comportamentos que quebram em silêncio
- [x] 03 Cadeias — 4 tipos de mensagem, `bind_tools` (pede, não executa), `tool_calls`
      dissecado, problema do overwrite em `messages`, `add_messages` + `MessagesState`
- [x] 04 Roteadores — `tools_condition` (porteiro), `ToolNode` (caixa), `ToolMessage`
      dissecado, tool fora da lista, exceção na tool, 2 pedidos de uma vez
- [x] 05 Agente ReAct — a volta `tools -> assistant`, loop pensar-agir-observar,
      condição de parada, `recursion_limit`, `SystemMessage` na chamada vs no estado
- [x] 06 Memória — estado transitório, `MemorySaver` + `thread_id`, reidratação,
      isolamento entre threads, `get_state`/`get_state_history`, `ValueError` sem thread
- [x] 07 Schemas — `TypedDict` (só hint), `dataclass` (atributo, sem fiscalizar),
      `Pydantic` (valida: `Literal` barra, validator normaliza)
- [x] 08 Reducers — `overwrite` vs `operator.add`, fan-out que quebra, custom
      tolerante a `None`, 3 poderes do `add_messages`, estado estendido
- [x] 09 Schemas Múltiplos — estado privado (viaja, some), `input_schema` /
      `output_schema` (nomes novos; `input=`/`output=` depreciados)

## Bloco 2 — módulos 3–4 do curso (aulas 10+)

- [x] 10 Filtro e corte — apagar do estado (`RemoveMessage`), filtrar só no
      `invoke`, cortar por tokens (`trim_messages`: system, `start_on`, parcial)
- [x] 11 Streaming — `stream` preguiçoso, modos `updates`/`values`/`messages`,
      `astream`, `astream_events` filtrado por nó
- [x] 12 Breakpoints — `interrupt_before`/`after`, `__interrupt__`,
      `get_state().next`, retomada com `stream(None, cfg)`
- [x] 13 Feedback humano — `update_state` (mesmo `id` corrige, sem `id` anexa),
      `as_node` + nó placeholder, correção de pedido parado
- [ ] 14 Breakpoints dinâmicos; 15 Viagem no tempo; 16 Paralelização;
      17 Sub-grafos; 18 Sub-grafos no LangSmith; 19 MapReduce

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

## No Colab (upload manual, um arquivo por vez)

O repo no GitHub é **privado**, então `git clone https://...` pede usuário/senha
e não funciona nas células do Colab. O fluxo oficial é upload manual:

1. Baixe o `.ipynb` da aula (página do arquivo no GitHub → `Raw` → salvar, ou
   `git pull` local + upload pelo painel de arquivos do Colab).
2. Faça upload no Colab (`Arquivo → Fazer upload de notebook`, ou arraste para
   o painel de arquivos).
3. **Rode a CÉLULA 0 primeiro** — todo notebook (01, 02 e os próximos) começa com
   ela: `%pip install -q ...` porque o Colab vem sem esses pacotes. Localmente,
   com `uv sync` feito, ela é inofensivo (no-op).
4. Cole a `GROQ_API_KEY` quando a célula pedir (digitação oculta, nada é salvo).
   Da Aula 03 em diante, todo notebook que usa Groq tem **célula de chave
   dedicada** (CÉLULA 1): sem chave ele segue no Fake offline.
5. Quando sair versão nova da aula: baixe de novo e repita (ou *Desconectar e
   descartar edições* antes, para nunca trabalhar em cima de versão velha).

> Nota: os badges "Abrir no Colab" no topo funcionam para o dono do repo logado
> com a integração GitHub do Colab; para terceiros dariam 404 enquanto o repo
> for privado.

Por que `get_llm` cai no Fake se o pacote faltar: sem isso, adicionar a chave
num Colab recém-criado estourava `ModuleNotFoundError` no meio da aula. Agora
ele avisa o comando de instalação e continua em modo offline.

## Estrutura

```
src/aula00_visao_geral.py   # lanchonete clássica + mesmo fluxo em StateGraph
src/aula01_setup.py         # get_llm() Groq-ou-Fake (tolera falta do pacote) + invoke/stream
src/aula02_grafo.py         # grafo de 3 nós + demos: overwrite, rota inexistente, chave fora do schema
notebooks/00_visao_geral.ipynb  # 11 células: analogia, 3 codes, dissecção, erros, desafio
notebooks/01_setup.ipynb        # 17 células: célula pip, uv vs pip, chave, raciocínio, stream, diagnóstico
notebooks/02_grafos.ipynb       # 30 células: célula pip, analogia, minimal, dissecção, 7 variações, exercício, desafio
src/aula03_cadeias.py         # cardápio [multiply, soma] + demos de overwrite/MessagesState
notebooks/03_cadeias.ipynb      # 20 células: célula pip, célula de chave, 4 mensagens, bind_tools, overwrite, MessagesState
src/aula04_roteador.py        # porteiro + caixa [multiply, soma] + demos de falha
notebooks/04_roteadores.ipynb   # 20 células: tools_condition, ToolNode, ToolMessage, 3 falhas, exercício, desafio
src/aula05_agente.py          # ReAct [add, multiply, divide] + demos sem-volta e limite de recursão
notebooks/05_agente_react.ipynb # 20 células: a volta, ciclo, traço real, trava, SYS, exercício, desafio
src/aula06_memoria.py         # ReAct + demos transitorio/memória/isolamento/sem-thread
notebooks/06_memoria.ipynb      # 20 células: sessão, prova do esquecimento, reidratação, raio-X, exercício, desafio
src/aula07_schemas.py         # mesmo grafo em TD/DC/PY + demos do bravo
notebooks/07_schemas.ipynb      # 19 células: 3 contratos, acesso, bravo, extra, normalizador, exercício, desafio
src/aula08_reducers.py        # overwrite, fan-out, operator.add, custom, add_messages, estendido
notebooks/08_reducers.ipynb     # 18 células: célula pip, quebra, [1,2,3,3], None, 3 poderes, exercício, desafio
src/aula09_schemas_multiplos.py # privado (baz) + in/out (notas) + sem-filtro
notebooks/09_schemas_multiplos.ipynb # 18 células: privado, in/out, contraste, KeyError, injeção, avaliador, fechamento
src/aula10_filtro_corte.py      # apagar, filtrar, trim, start_on, parcial, filter por tipo
notebooks/10_filtro_corte.ipynb   # 19 células: comanda, 3 táticas, system/start_on/parcial, exercício, desafio
src/aula11_streaming.py       # ReAct + demos updates/values/messages/tokens reais
notebooks/11_streaming_hitl.ipynb # 21 células: rastreio, 3 modos, gerador, async, filtro por nó, desafio
src/aula12_breakpoints.py      # fiscal: pausa/inspeciona/retoma + sem-sessão + after
notebooks/12_breakpoints.ipynb  # 18 células: fiscal, pausa, carimbo, sem-sessão, after, exercício, desafio
src/aula13_feedback.py        # corrige pedido, anexa contexto, feedback assinado, as_node fantasma
notebooks/13_feedback_humano.ipynb # 18 células: caneta vermelha, correção, anexo, as_node, placeholder, exercício, desafio
tests/test_aula00.py ...    # offline, determinístico
```

## Comportamentos verificados na Aula 02 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| roteador devolve nome inexistente | aviso `wrote to unknown channel branch:to:X, ignoring it` e **encerra sem erro** |
| nó devolve chave fora do `TypedDict` | chave **ignorada** em silêncio |
| `invoke` sem uma chave do estado | `KeyError` só quando um nó tenta ler |
| dois nós escrevem a mesma chave em sequência | **último ganha** (`overwrite`); em paralelo, `InvalidUpdateError` (Aula 08) |
| nó muta `state` e devolve `{}` | mudança **não** persiste |
| aresta para nó inexistente / nó duplicado / sem `START` | `ValueError` na construção |
| `Literal` no retorno do roteador | é **só hint** — `str` simples funciona |
| `draw_ascii()` | exige `grandalf` (não instalado); `draw_mermaid()` sempre funciona |

## Comportamentos verificados na Aula 04 (LangGraph 1.2.x, Groq gpt-oss-20b)

| Situação | O que realmente acontece |
|---|---|
| `tools_condition` com `tool_calls` | devolve `"tools"`; sem, devolve `"__end__"` |
| `ToolNode` executa | um `ToolMessage` por pedido, `content` sempre string (`12` vira `'12'`) |
| `tool_call_id` do recibo | **igual ao `id`** do pedido (grampo recibo-pedido) |
| tool fora da lista do `ToolNode` | **não quebra**: `ToolMessage` com `Error: ... is not a valid tool` |
| exceção **dentro** da tool (`1/0`) | **propaga** (`ZeroDivisionError` mata o `invoke`) |
| dois `tool_calls` juntos | dois `ToolMessage`, cada um com seu `id` |

## Comportamentos verificados na Aula 05 (LangGraph 1.2.x, Groq gpt-oss-20b)

| Situação | O que realmente acontece |
|---|---|
| aresta `tools -> assistant` | cria o loop; sem ela (Aula 04), o recibo nunca é relido |
| 3 contas encadeadas | `add(3,4)=7` → modelo fez `7×2=14` de cabeça → `divide(14,5)=2.8` → frase final (decomposição é do LLM, afirme o resultado) |
| `recursion_limit` estourado | `GraphRecursionError: Recursion limit of N reached...` (padrão: 25) |
| `SystemMessage` só na chamada | não polui o estado; gravado no estado, viaja no histórico |

## Comportamentos verificados na Aula 06 (LangGraph 1.2.x, Groq gpt-oss-20b)

| Situação | O que realmente acontece |
|---|---|
| 2 `invoke`s sem checkpointer | "dois universos": turno 2 (real) chutou `2` sem nunca ter visto o `7` |
| mesma `thread_id` + checkpointer | turno 2 reidrata: `7` → `14`, estado com 8 mensagens |
| `thread_id` diferente | isolamento total (a outra thread não vê nada) |
| grafo com checkpointer sem `config` | `ValueError: Checkpointer requires ... thread_id ...` |
| `get_state_history` | um checkpoint por passo (10 na conversa de 2 turnos) |
| `MemorySaver` | RAM: morre com o processo (produção: SQLite/Postgres) |

## Comportamentos verificados na Aula 07 (LangGraph + Pydantic v2)

| Situação | O que realmente acontece |
|---|---|
| `mood="bravo"` no `TypedDict`/`dataclass` | entra, circula e sai — silêncio total |
| `mood="bravo"` no Pydantic | `ValidationError` na **construção** (`literal_error`) |
| `@field_validator` com `Literal` | o `Literal` barra primeiro; o custom serve para normalizar |
| nó em grafo DC/PY | recebe a **instância** (`state.name`); resultado do `invoke` é **dict** |
| chave extra no Pydantic | **ignorada** por padrão (sem erro) |

## Comportamentos verificados na Aula 08 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| fan-out sem reducer | `InvalidUpdateError: At key 'foo': Can receive only one value per step...` |
| fan-out com `operator.add` | acumula: `[1]` → `[1, 2]` → `[1, 2, 3, 3]` (paralelos leem o mesmo retrato) |
| `add` com `None` | `TypeError: can only concatenate list (not "NoneType") to list` |
| reducer custom | tolera `None`, limita, mescla "à sua maneira" |
| `add_messages` por `id` igual | **substitui** em vez de anexar; `RemoveMessage(id)` apaga |

## Comportamentos verificados na Aula 09 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| estado privado | `baz` existe no `stream` (`{'no_1': {'baz': 10}}`), some no `invoke` (`{'foo': 11}`) |
| `input_schema`/`output_schema` | entra `pergunta`, sai só `resposta`; `notas` vivem e morrem dentro |
| sem filtro | tudo vaza (`pergunta`, `resposta` e `notas`) |
| nó lendo fora do próprio schema | `KeyError` (cada nó enxerga só o declarado) |
| `input=`/`output=` (nomes do curso) | funcionam, mas emitem `LangGraphDeprecatedSinceV05` (usar `input_schema=`) |

## Comportamentos verificados na Aula 10 (langchain-core 1.6.x)

| Situação | O que realmente acontece |
|---|---|
| `RemoveMessage` no estado | apaga de verdade (próximos turnos não veem); exige `id` + reducer |
| filtro só no `invoke` | estado intacto (6 msgs), LLM vê recorte (1 msg) |
| `trim` sem `include_system` | SYS cai junto; com, é preservado fora do teto |
| `start_on="human"` + teto apertado | descarta até sobrar quase nada (aqui: só o system) |
| `allow_partial=True` | salva o **fim** da longa (por linhas); de 1 linha só, cai inteira |
| `token_counter=len` | conta **mensagens**, não tokens — usar tiktoken/contador do modelo |

## Comportamentos verificados na Aula 11 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| `stream` criado, não iterado | nada executa (gerador preguiçoso); 2ª passada vem vazia |
| `updates` / `values` / `messages` | delta por nó / estado completo / tupla (chunk + `langgraph_node`) |
| `asyncio.run()` no notebook | `RuntimeError` (kernel já tem loop); usar `await` direto, `asyncio.run` só em `.py` |
| Fake criado dentro do nó com loop | cada volta zera a sequência → loop infinito (construir fora, reusar dentro) |

## Comportamentos verificados na Aula 12 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| `interrupt_before=["tools"]` | pausa antes do nó; chunk `__interrupt__`; `next == ("tools",)` |
| `stream(None, cfg)` | retoma do checkpoint; ao fim, `next == ()` |
| interrupt sem checkpointer | pausa sim; retomar com `None` morre (`EmptyInputError`) |
| `interrupt_after=["assistant"]` | pausa depois do nó; aqui para no mesmo ponto |
| Fake reusado entre grafos | sequência embaralhada (um Fake fresco por grafo) |

## Comportamentos verificados na Aula 13 (LangGraph 1.2.x)

| Situação | O que realmente acontece |
|---|---|
| `update_state` com mesmo `id` | sobrescreve (corrige o pedido; recibo `30` prova) |
| `update_state` sem `id` | anexa (contexto novo; pedido original continua) |
| `as_node` com nome inexistente | `InvalidUpdateError: Node ... does not exist` |
| placeholder + `as_node` | pausa antes dele; edição entra assinada; fluxo segue normal |

## O que a Aula 00 ensina

| Conceito | Tradução dev clássico |
|---|---|
| Estado | dict compartilhado (`TypedDict` = contrato) |
| Nó | função `f(state)->update parcial` |
| Aresta | ordem fixa `A -> B` |
| Aresta condicional | seu `if`, retorna nome do próximo nó |
| `compile/invoke` | montar fluxograma / rodar do `START` ao `END` |
| Chain vs Graph | cano reto vs fluxograma com ciclo/decisão runtime |
