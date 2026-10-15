# Reforço LangGraph — do zero ao MapReduce

**Aprenda LangGraph como quem aprende a cozinhar: um conceito por vez, com a mão na massa.**

Este repositório é um curso de reforço sobre **LangGraph** — a ferramenta que transforma um modelo de linguagem (que só "conversa") em um **agente que executa tarefas**: ele consulta ferramentas, lembra de conversas passadas, pede aprovação humana antes de agir e organiza trabalhos em paralelo.

Cada aula é um notebook independente que você abre no Colab e executa célula por célula. Tudo é explicado com analogias de uma lanchonete (pedidos, caixa, fiscal, cozinha) e com código comentado linha a linha — sem matemática, sem pressa. Quando o assunto precisa de inteligência artificial de verdade usamos o Groq (gratuito); quando dá para aprender só com a mecânica, roda 100% offline, sem chave e sem custo.

Ao final das 20 aulas você saberá montar um agente completo: que entende pedidos fora de ordem, usa ferramentas, lembra entre mensagens, pede aprovação quando precisa e organiza tarefas paralelas — a base para aplicar no seu próprio projeto (como um avaliador automático de redações).

Este reforço foi baseado no curso da **Scoras Academy**, do professor **Anderson Amaral** — os temas seguem a trilha original; todos os exemplos, textos e códigos aqui são próprios. Ficam os devidos créditos:

Professor Anderson Amaral
LinkedIn: https://www.linkedin.com/in/andersonlamaral

Scoras Academy
Site: https://scorasacademy.com.br
GitHub (Somente para Alunos): https://github.com/Scoras-Academy

Padrão técnico: Groq como LLM primário (`GROQ_API_KEY` via `.env`, nunca versionado), modelo `openai/gpt-oss-20b` sempre com `reasoning_effort="low"`. Sem chave, tudo roda **offline** com Fake determinístico. Regras do projeto em [`AGENTS.md`](AGENTS.md).

## Aulas

| # | Aula | Resenha | Abrir no Colab |
|---|---|---|---|
| 00 | Visão Geral | O mapa do curso: o que é um grafo, por que um `if/else` não basta quando entra IA, e a diferença entre uma corrente reta e um fluxograma com voltas. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/00_visao_geral.ipynb) |
| 01 | Setup | Preparar o ambiente (instalador `uv`, chave do Groq guardada com segurança) e fazer a primeira pergunta ao modelo, entendendo resposta pronta vs resposta pingando. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/01_setup.ipynb) |
| 02 | Grafos | Montar e rodar seu primeiro fluxograma: etapas, bifurcações e o que acontece quando dois caminhos escrevem no mesmo lugar. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/02_grafos.ipynb) |
| 03 | Cadeias | Transformar conversa em lista de mensagens e ensinar o modelo a *pedir* uma ferramenta (sem executar ainda). | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/03_cadeias.ipynb) |
| 04 | Roteadores | Colocar um "porteiro" que decide: executa a ferramenta ou encerra — e ver o primeiro cálculo real acontecer. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/04_roteadores.ipynb) |
| 05 | Agente ReAct | Fechar o ciclo: o modelo lê o resultado, pede mais ferramentas e só para quando termina — o coração de todo agente. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/05_agente_react.ipynb) |
| 06 | Memória | Fazer o agente lembrar entre mensagens (como sessão de site), com conversas separadas por cliente. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/06_memoria.ipynb) |
| 07 | Schemas | Contratos para os dados do grafo: do rascunho que aceita tudo ao validador que barra valor inválido. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/07_schemas.ipynb) |
| 08 | Reducers | Regras de mesclagem quando duas etapas escrevem juntas, e os três poderes de manipular o histórico. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/08_reducers.ipynb) |
| 09 | Schemas Múltiplos | Esconder o interior: o grafo recebe pouco, usa segredos por dentro e devolve só o essencial. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/09_schemas_multiplos.ipynb) |
| 10 | Filtro e corte | Impedir que conversas longas estourem o custo: apagar, recortar ou podar o histórico por orçamento. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/10_filtro_corte.ipynb) |
| 11 | Streaming | Ver o agente trabalhando ao vivo (por etapa, foto atual ou pingos de resposta) em vez de esperar o final. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/11_streaming_hitl.ipynb) |
| 12 | Breakpoints | Pausar o agente antes de executar para um humano aprovar — e retomar de onde parou. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/12_breakpoints.ipynb) |
| 13 | Feedback humano | Deixar o humano corrigir e reescrever o que está parado, assinando a intervenção. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/13_feedback_humano.ipynb) |
| 14 | Breakpoints dinâmicos | Pausar por regra (ex: só conta alta) em vez de pausar tudo, com a API nova de pergunta-e-resposta. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/14_breakpoints_dinamicos.ipynb) |
| 15 | Viagem no tempo | Rebobinar a execução: rever o passado, repetir cenas e testar futuros alternativos. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/15_viagem_tempo.ipynb) |
| 16 | Paralelização | Rodar ramos juntos (cozinha e bar) e juntar os resultados, inclusive buscando em duas fontes ao mesmo tempo. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/16_paralelizacao.ipynb) |
| 17 | Sub-grafos | Quebrar o grafo em equipes (grafos dentro de grafos) com interfaces que não vazam segredo. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/17_subgrafos.ipynb) |
| 18 | Observabilidade | Enxergar quem chamou quem, quanto tempo levou e onde quebrou — localmente ou na nuvem. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/18_langsmith.ipynb) |
| 19 | MapReduce | Quando o número de tarefas só se conhece executando: espalhar N trabalhos e juntar no final. Fecha o curso. | [abrir](https://colab.research.google.com/github/fcervan/reforco-langgraph/blob/main/notebooks/19_mapreduce.ipynb) |

> Nota: o repo no GitHub é privado — os links acima abrem para o dono logado com a integração GitHub do Colab; para terceiros dariam 404.

## Uso rápido

```bash
pip install -r requirements.txt
# ou com uv (recomendado): uv venv && uv sync
python src/aula00_visao_geral.py   # sem LLM, 100% offline
python src/aula01_setup.py         # Groq real com GROQ_API_KEY, senão Fake
python -m pytest tests/ -q         # 116 testes (offline + Groq real)
jupyter notebook notebooks/00_visao_geral.ipynb
```

Com Groq real (a partir da Aula 01):

```bash
cp .env.example .env  # preencher GROQ_API_KEY
```

## No Colab (upload manual, um arquivo por vez)

O repo no GitHub é **privado**, então `git clone https://...` pede usuário/senha e não funciona nas células do Colab. O fluxo oficial é upload manual (ou abrir pelos links da tabela acima):

1. Baixe o `.ipynb` da aula (página do arquivo no GitHub → `Raw` → salvar), ou abra direto pelo link "abrir" da tabela.
2. Faça upload no Colab (`Arquivo → Fazer upload de notebook`, ou arraste para o painel de arquivos).
3. **Rode a CÉLULA 0 primeiro** — todo notebook começa com ela: `%pip install -q ...` porque o Colab vem sem esses pacotes. Localmente, com `uv sync` feito, ela é inofensiva (no-op).
4. Cole a `GROQ_API_KEY` quando a célula pedir (digitação oculta, nada é salvo). Da Aula 03 em diante, todo notebook que usa Groq tem **célula de chave dedicada** (CÉLULA 1): sem chave ele segue no Fake offline.
5. Quando sair versão nova da aula: baixe de novo e repita (ou *Desconectar e descartar edições* antes, para nunca trabalhar em cima de versão velha).

Por que `get_llm` cai no Fake se o pacote faltar: sem isso, adicionar a chave num Colab recém-criado estourava `ModuleNotFoundError` no meio da aula. Agora ele avisa o comando de instalação e continua em modo offline.

## Estrutura

```
AGENTS.md                 # regras do projeto (modelo, padrão de aula, git, Colab)
src/aulaNN_*.py           # espelho executável de cada aula (python src/...)
notebooks/NN_*.ipynb      # 1 notebook autocontido por aula (CÉLULA 0 instala tudo)
tests/test_aulaNN.py      # testes offline e determinísticos (+ Groq real marcado)
```

## Comportamentos verificados (clique para expandir)

Cada tabela abaixo foi executada de verdade no ambiente indicado — não é documentação copiada, é comportamento medido.

<details><summary>Aula 02 — Grafos (LangGraph 1.2.x)</summary>

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

</details>

<details><summary>Aula 04 — Roteadores (LangGraph 1.2.x, Groq gpt-oss-20b)</summary>

| Situação | O que realmente acontece |
|---|---|
| `tools_condition` com `tool_calls` | devolve `"tools"`; sem, devolve `"__end__"` |
| `ToolNode` executa | um `ToolMessage` por pedido, `content` sempre string (`12` vira `'12'`) |
| `tool_call_id` do recibo | **igual ao `id`** do pedido (grampo recibo-pedido) |
| tool fora da lista do `ToolNode` | **não quebra**: `ToolMessage` com `Error: ... is not a valid tool` |
| exceção **dentro** da tool (`1/0`) | **propaga** (`ZeroDivisionError` mata o `invoke`) |
| dois `tool_calls` juntos | dois `ToolMessage`, cada um com seu `id` |

</details>

<details><summary>Aula 05 — Agente ReAct (LangGraph 1.2.x, Groq gpt-oss-20b)</summary>

| Situação | O que realmente acontece |
|---|---|
| aresta `tools -> assistant` | cria o loop; sem ela (Aula 04), o recibo nunca é relido |
| 3 contas encadeadas | `add(3,4)=7` → modelo fez `7×2=14` de cabeça → `divide(14,5)=2.8` → frase final (decomposição é do LLM, afirme o resultado) |
| `recursion_limit` estourado | `GraphRecursionError: Recursion limit of N reached...` (padrão: 25) |
| `SystemMessage` só na chamada | não polui o estado; gravado no estado, viaja no histórico |

</details>

<details><summary>Aula 06 — Memória (LangGraph 1.2.x, Groq gpt-oss-20b)</summary>

| Situação | O que realmente acontece |
|---|---|
| 2 `invoke`s sem checkpointer | "dois universos": turno 2 (real) chutou `2` sem nunca ter visto o `7` |
| mesma `thread_id` + checkpointer | turno 2 reidrata: `7` → `14`, estado com 8 mensagens |
| `thread_id` diferente | isolamento total (a outra thread não vê nada) |
| grafo com checkpointer sem `config` | `ValueError: Checkpointer requires ... thread_id ...` |
| `get_state_history` | um checkpoint por passo (10 na conversa de 2 turnos) |
| `MemorySaver` | RAM: morre com o processo (produção: SQLite/Postgres) |

</details>

<details><summary>Aula 07 — Schemas (LangGraph + Pydantic v2)</summary>

| Situação | O que realmente acontece |
|---|---|
| `mood="confuso"` no `TypedDict`/`dataclass` | entra, circula e sai — silêncio total |
| `mood="confuso"` no Pydantic | `ValidationError` na **construção** (`literal_error`) |
| `@field_validator` com `Literal` | o `Literal` barra primeiro; o custom serve para normalizar |
| nó em grafo DC/PY | recebe a **instância** (`state.name`); resultado do `invoke` é **dict** |
| chave extra no Pydantic | **ignorada** por padrão (sem erro) |

</details>

<details><summary>Aula 08 — Reducers (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| fan-out sem reducer | `InvalidUpdateError: At key 'foo': Can receive only one value per step...` |
| fan-out com `operator.add` | acumula: `[1]` → `[1, 2]` → `[1, 2, 3, 3]` (paralelos leem o mesmo retrato) |
| `add` com `None` | `TypeError: can only concatenate list (not "NoneType") to list` |
| reducer custom | tolera `None`, limita, mescla "à sua maneira" |
| `add_messages` por `id` igual | **substitui** em vez de anexar; `RemoveMessage(id)` apaga |

</details>

<details><summary>Aula 09 — Schemas Múltiplos (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| estado privado | `acrescimo` existe no `stream` (`{'calcula_taxa': {'acrescimo': 10}}`), some no `invoke` (`{'subtotal': 110}`) |
| `input_schema`/`output_schema` | entra `pergunta`, sai só `resposta`; `notas` vivem e morrem dentro |
| sem filtro | tudo vaza (`pergunta`, `resposta` e `notas`) |
| nó lendo fora do próprio schema | `KeyError` (cada nó enxerga só o declarado) |
| `input=`/`output=` (nomes do curso) | funcionam, mas emitem `LangGraphDeprecatedSinceV05` (usar `input_schema=`) |

</details>

<details><summary>Aula 10 — Filtro e corte (langchain-core 1.6.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `RemoveMessage` no estado | apaga de verdade (próximos turnos não veem); exige `id` + reducer |
| filtro só no `invoke` | estado intacto (6 msgs), LLM vê recorte (1 msg) |
| `trim` sem `include_system` | SYS cai junto; com, é preservado fora do teto |
| `start_on="human"` + teto apertado | descarta até sobrar quase nada (aqui: só o system) |
| `allow_partial=True` | salva o **fim** da longa (por linhas); de 1 linha só, cai inteira |
| `token_counter=len` | conta **mensagens**, não tokens — usar tiktoken/contador do modelo |

</details>

<details><summary>Aula 11 — Streaming (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `stream` criado, não iterado | nada executa (gerador preguiçoso); 2ª passada vem vazia |
| `updates` / `values` / `messages` | delta por nó / estado completo / tupla (chunk + `langgraph_node`) |
| `asyncio.run()` no notebook | `RuntimeError` (kernel já tem loop); usar `await` direto, `asyncio.run` só em `.py` |
| Fake criado dentro do nó com loop | cada volta zera a sequência → loop infinito (construir fora, reusar dentro) |

</details>

<details><summary>Aula 12 — Breakpoints (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `interrupt_before=["tools"]` | pausa antes do nó; chunk `__interrupt__`; `next == ("tools",)` |
| `stream(None, cfg)` | retoma do checkpoint; ao fim, `next == ()` |
| interrupt sem checkpointer | pausa sim; retomar com `None` morre (`EmptyInputError`) |
| `interrupt_after=["assistant"]` | pausa depois do nó; aqui para no mesmo ponto |
| Fake reusado entre grafos | sequência embaralhada (um Fake fresco por grafo) |

</details>

<details><summary>Aula 13 — Feedback humano (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `update_state` com mesmo `id` | sobrescreve (corrige o pedido; recibo `30` prova) |
| `update_state` sem `id` | anexa (contexto novo; pedido original continua) |
| `as_node` com nome inexistente | `InvalidUpdateError: Node ... does not exist` |
| placeholder + `as_node` | pausa antes dele; edição entra assinada; fluxo segue normal |

</details>

<details><summary>Aula 14 — Breakpoints dinâmicos (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `raise NodeInterrupt(motivo)` | pausa com motivo em `tasks[].interrupts[].value`; **depreciado** (sai na v2.0) |
| retomar sem mudar | reexecuta o nó → pausa de novo (preso; saída: `update_state` ou `Command`) |
| `interrupt(motivo)` + `Command(resume=R)` | a chamada devolve `R` na retomada (humano responde no fluxo) |
| estático vs régua em conta baixa | lista fixa pausa à toa; régua deixa passar |

</details>

<details><summary>Aula 15 — Viagem no tempo (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| `get_state_history` | do mais novo (`[0]` = atual) ao mais antigo (`__start__`, vazio) |
| replay `stream(None, config_antiga)` | reexecuta a partir dali; passado intacto (com LLM real pode divergir) |
| fork com mesmo `id` | substitui a mensagem; com id novo, anexa (duplica) |
| após `update_state` no passado | nada executa até `stream(None, fork_config)`; `get_state` mostra o ramo novo |

</details>

<details><summary>Aula 16 — Paralelização (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| fan-out simétrico → join | espera os 2 ramos; join roda **1x** |
| fan-out desigual → join | **1x por chegada** (2x); 2ª execução vê o efeito da 1ª |
| `sorting_reducer` | mesma saída ordenada nas 3 execuções (fim da loteria) |
| RAG paralelo | 2 fontes juntas + 1 síntese (Groq real cita valores; Fake conta fontes) |

</details>

<details><summary>Aula 17 — Sub-grafos (LangGraph 1.2.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| nó-filho compilado | lê filtrado pelo schema dele; devolve estado final COMPLETO (eco incluso) |
| 2 filhos paralelos, chave comum | `InvalidUpdateError` (eco duplo na mesma etapa) |
| reducer na chave comum | evita o crash, mas o eco duplica (`'pastelpastelpastel'`) |
| `output_schema` no filho | só as chaves declaradas voltam; privado não vaza; `pedido` intacto |

</details>

<details><summary>Aula 18 — Observabilidade (langchain-core 1.6.x)</summary>

| Situação | O que realmente acontece |
|---|---|
| callback `on_chain_start` | `serialized=None`; nome vem em `name=`, nó em `metadata['langgraph_node']` |
| árvore local | indentação por `parent_run_id`; raiz fecha por último (ordem de término) |
| erro no filho | `on_chain_error` em cada nível até o pai; `stream` propaga a exceção |
| LangSmith sem chave | nada a fazer; com `LANGCHAIN_TRACING_V2=true` + chave, mesmo código traça |

</details>

<details><summary>Aula 19 — MapReduce (LangGraph 1.2.x, Groq gpt-oss-20b)</summary>

| Situação | O que realmente acontece |
|---|---|
| condicional devolve lista de `Send` | 1 execução por `Send`; N decidido em runtime (stream mostra N `avalia`) |
| `langgraph.constants.Send` | funciona, mas emite `LangGraphDeprecatedSinceV10` (usar `langgraph.types`) |
| `with_structured_output(Pydantic)` | objeto tipado (`item`, `nota: int` validado) |
| reduce final com N=0 | `IndexError` sem guarda — todo `elege` precisa de fallback |

</details>

## O que a Aula 00 ensina

| Conceito | Tradução dev clássico |
|---|---|
| Estado | dict compartilhado (`TypedDict` = contrato) |
| Nó | função `f(state)->update parcial` |
| Aresta | ordem fixa `A -> B` |
| Aresta condicional | seu `if`, retorna nome do próximo nó |
| `compile/invoke` | montar fluxograma / rodar do `START` ao `END` |
| Chain vs Graph | cano reto vs fluxograma com ciclo/decisão runtime |
