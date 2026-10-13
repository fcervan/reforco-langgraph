# AGENTS.md — reforco-langgraph

Regras operacionais deste projeto. Valem para todas as aulas (00–09) e qualquer
correção futura. Em caso de conflito com o `AGENTS.md` da raiz, vale este aqui.

## Modelo e provider

- Provider: **Groq** (`GROQ_API_KEY`, nunca versionada, nunca impressa, nunca em chat).
- Modelo padrão: **`openai/gpt-oss-20b`** — em `src/`, notebooks, testes e README.
- Sempre passar **`reasoning_effort="low"`** ao instanciar `ChatGroq` (o gpt-oss é
  modelo de raciocínio; sem isso ele gasta o orçamento pensando, estoura em
  `finish_reason: length` e devolve `content` vazio — ver Aula 01, seção 3.1).
- `temperature=0` em tudo que envolve tools/grafos; `0.9` só em demo criativa.
- Todo código com LLM tem fallback **Fake offline** (`FakeMessagesListChatModel`)
  quando não há chave — a aula nunca pode "morrer" sem chave.
- `get_llm` deve tolerar `ImportError` do `langchain_groq` (Colab recém-criado):
  avisar o comando de instalação e cair no Fake.

## Padrão de cada notebook (didático, dev clássico)

- **Autocontido**: funciona com 1 upload no Colab (não importar de `src/`).
- **CÉLULA 0**: `%pip install -q ...` (inofensiva local com `uv sync` feito).
- **Célula de chave** (obrigatória da Aula 03 em diante em todo notebook que
  usa Groq): tenta `os.getenv` → `.env` (`load_dotenv`) → `getpass.getpass`
  interativo → segue no Fake se nada funcionar. **Nunca** dar `print` na chave,
  só em presença (`True/False`).
- Estrutura em seções: analogia dev clássico → conceito → código mínimo →
  dissecção linha a linha → variações que quebram (testadas de verdade) →
  erros clássicos → exercício guiado → desafio → checklist.
- **Português com acentuação correta** em markdown, comentários e strings de
  exibição. Exceções (são código): identificadores, `resposta_direta`-style,
  `tool_call_id`, `call_1`, nomes de função.
- Comportamentos "surpreendentes" documentados só se **executados e verificados**
  no ambiente (versão do LangGraph registrada no README).
- Sem outputs versionados: notebooks commitados **limpos** (`outputs: []`,
  `execution_count: null`). Nunca commitar output de execução do Colab.

## Código e testes

- Espelho em `src/aulaNN_*.py` executável (`python src/...`) + demos nomeadas.
- `tests/test_aulaNN.py` offline e determinístico (chave real só em teste
  marcado com `skipif`, nunca obrigatório).
- Validar sempre: `pytest`, `nbconvert --execute` com **0 erros** (com e sem
  chave quando aplicável), `00_visao_geral.ipynb` intacto (conferir md5
  `f05eb1634396155a7be96301656286bc`).

## README e git

- Todo commit que muda aula/código atualiza o `README.md` (status, estrutura,
  badges "Abrir no Colab" para cada notebook novo, tabela de comportamentos
  quando a aula descobrir algum).
- `.env` nunca entra no git (já no `.gitignore`, junto de `__pycache__/`,
  `.pytest_cache/`, `.venv/`).
- Nunca `git add/commit/push` sem confirmação explícita; ao confirmar, mostrar
  a saída do push. Diante de `rejected` (ex: save do Colab no remoto),
  inspecionar o commit estranho antes de `rebase` — nunca `--force`.
- Fluxo Colab oficial: **upload manual** (repo privado não permite `git clone`
  sem token). Não orientar clone; não pedir "Salvar no GitHub" pelo Colab
  (grava outputs e conflita).
