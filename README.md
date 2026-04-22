# Cortex — Memória Local de Código para o Claude

> Um grafo de conhecimento self-hosted que dá ao Claude memória persistente sobre seus projetos — com um visualizador 3D interativo.

![RAG Viewer](https://img.shields.io/badge/viewer-grafo_3D-58a6ff?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9+-3fb950?style=flat-square)
![License](https://img.shields.io/badge/licença-MIT-bc8cff?style=flat-square)
![No cloud](https://img.shields.io/badge/cloud-nenhum-ff9f1a?style=flat-square)
![Made in Brazil](https://img.shields.io/badge/feito%20no-Brasil%20🇧🇷-009c3b?style=flat-square)

---

## O problema

Toda vez que você abre uma nova sessão no Claude Code, ele começa do zero. Você explica a stack de novo. Re-descreve a arquitetura. Cola os mesmos caminhos de arquivo de sempre. O Claude é inteligente, mas não tem memória — e essa re-explicação constante desperdiça tempo e quebra o raciocínio.

A solução mais comum é jogar tudo no `CLAUDE.md`. Mas isso vira uma bagunça rápido: sem estrutura, sem automação, desatualizado assim que o código muda, e você ainda escreve tudo na mão.

---

## A ideia

E se o Claude sempre soubesse do seu projeto — os arquivos, as funções, as dependências, as decisões que você tomou semana passada — sem você precisar explicar de novo?

É isso que o Cortex faz. Um **grafo de conhecimento local** que fica do lado dos seus projetos:

- Escaneia o código e monta um mapa estruturado de arquivos, funções, classes e imports
- Detecta automaticamente sua stack (Node.js, Python, Go, Rust, Docker…) e gera um resumo do projeto
- Mantém logs de sessão — o que o Claude trabalhou cada dia, o que foi decidido, o que vem a seguir
- Injeta contexto no `CLAUDE.md` para o Claude ler o grafo antes de responder **qualquer coisa**
- Serve um **visualizador 3D interativo** — orbite, zoom, clique nos nós, veja as conexões ao vivo

Tudo roda localmente. Sem chamadas de API, sem cloud, sem assinatura.

---

## Como foi feito

O objetivo foi manter o mais simples possível — sem frameworks, sem build step, sem gerenciador de pacotes. Só Python e JS puro.

O script de sync (`scripts/sync.py`) lê os arquivos do projeto usando o módulo `ast` do Python para código Python e regex para JS/TS. Percorre a árvore de diretórios, extrai nós (arquivos, funções, classes) e arestas (imports, definições), e escreve um `graph.json`. Também lê os arquivos de config — `package.json`, `pyproject.toml`, `go.mod`, `.env.example` — e gera um `RESUMO.md` com stack, scripts e variáveis de ambiente já preenchidos.

O visualizador (`viewer/app.js`) usa o [3d-force-graph](https://github.com/vasturiano/3d-force-graph) — um grafo de força 3D em WebGL — para renderizar o código como um átomo vivo que você pode orbitar e explorar. Os nós são dimensionados pela quantidade de conexões. As arestas de import têm partículas animadas fluindo por elas. Clique num nó e um painel de detalhes desliza mostrando tudo que ele importa e tudo que o usa.

A injeção no `CLAUDE.md` força o Claude a imprimir um bloco de contexto formatado no início de cada sessão — stack, contagem de arquivos, data do último sync, resumo do projeto — antes de responder qualquer coisa.

---

## Demo

```
┌─ Cortex Viewer (localhost:7842) ───────────────────────────────────┐
│                                                                      │
│  [Explorer]        [  ●  grafo 3D — orbite com o mouse  ●  ]       │
│  ▼ src                                                               │
│    ▼ api           Nós brilham por grupo: api · service · model     │
│      users.ts  5   Partículas fluem pelas arestas de import         │
│        ƒ getUser   Clique num nó → painel de detalhes desliza       │
│        ƒ create                                                      │
│    ▶ services   [ Logs ]   ── logs diários de sessão ──             │
│    ▶ models     [ Memory ] ── RESUMO.md do projeto ──               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Como funciona

```
~/Dev/Rag/                     ← este repo
│
├── scripts/
│   ├── sync.py                ← escaneia um projeto e grava os dados
│   └── graph_gen.py           ← parser AST (JS/TS/Python)
│
├── viewer/                    ← visualizador 3D (servido via HTTP)
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── projects.json              ← índice de todos os projetos sincronizados
│
└── <nome-do-projeto>/         ← uma pasta por projeto
    ├── graph/graph.json       ← grafo do código (gerado automaticamente)
    ├── memory/RESUMO.md       ← resumo do projeto (gerado + editável)
    └── logs/
        ├── activity.md        ← histórico de syncs
        └── 2024-01-15.md      ← log diário de sessão

~/Dev/meu-projeto/             ← seu projeto real (não é modificado)
    └── CLAUDE.md              ← instruções RAG injetadas aqui
```

Seus projetos reais **nunca são modificados**, exceto o `CLAUDE.md`.

---

## Início rápido

### 1. Clone este repo

```bash
git clone https://github.com/koalitos/cortex ~/Dev/Rag
```

Sem dependências para instalar — apenas Python 3.9+ (biblioteca padrão).

### 2. Sincronize um projeto

```bash
python3 ~/Dev/Rag/rag /caminho/para/meu-projeto
```

Isso vai:
- Parsear todos os arquivos `.js`, `.ts`, `.jsx`, `.tsx`, `.py` e gerar o grafo
- Detectar a stack a partir de `package.json`, `pyproject.toml`, `go.mod`, etc.
- Criar `<projeto>/memory/RESUMO.md` já preenchido com stack, scripts e variáveis de ambiente
- Escrever um `CLAUDE.md` no projeto forçando o Claude a carregar o contexto a cada sessão
- Criar um log diário em `<projeto>/logs/AAAA-MM-DD.md`

### 3. Inicie o visualizador

```bash
python3 ~/Dev/Rag/rag --serve
```

Abre `http://localhost:7842` automaticamente. O grafo 3D é interativo:
- **Arrastar** para orbitar, **scroll** para zoom
- **Clicar** num nó para ver suas conexões no painel de detalhes
- **Hover** para tooltip com nome, tipo e caminho do arquivo
- **Sidebar** mostra a árvore de pastas real com funções aninhadas sob os arquivos
- Botão **Memory** mostra o RESUMO.md do projeto
- Botão **Logs** mostra os logs diários de sessão

### 4. Ver status dos projetos

```bash
python3 ~/Dev/Rag/rag --status
```

---

## Integração com Claude Code

Após o sync, o `CLAUDE.md` do seu projeto vai conter:

```markdown
## RAG — Contexto obrigatório

REGRA ABSOLUTA: no início de cada sessão, ANTES de responder qualquer coisa, você DEVE:

1. Ler os arquivos listados abaixo em ordem
2. Imprimir um bloco de contexto:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RAG carregado: meu-projeto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Stack:      Node.js + TypeScript, NestJS, Prisma
  Arquivos:   205 arquivos · 102 funções · 198 classes
  Último sync: 2024-01-15 14:32
  Memória:    API REST para autenticação de usuários...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

O Claude lê o grafo, a memória e os logs **antes de cada resposta** — e sempre conhece o projeto sem você re-explicar.

### Skills para Claude Code (opcional)

Adicione no seu `~/.claude/CLAUDE.md` global para atalhos de slash command:

**`/salvar-grafo`** — re-sincroniza o grafo e adiciona um resumo de sessão no log do dia:
```markdown
# salvar-grafo
Quando o usuário digitar `/salvar-grafo`, rode sync.py para o projeto atual e
adicione um bloco de sessão em logs/AAAA-MM-DD.md com o que foi feito.
```

**`/retomar-grafo`** — carrega o contexto completo do projeto no início da sessão:
```markdown
# retomar-grafo
Quando o usuário digitar `/retomar-grafo`, leia a memória RAG, o log diário recente
e as stats do grafo, depois imprima um resumo de contexto formatado.
```

---

## Stack detectada automaticamente

O `sync.py` lê os arquivos do projeto e preenche o `memory/RESUMO.md` automaticamente:

| Arquivo | O que é detectado |
|---------|------------------|
| `package.json` | Runtime (Node/Bun), linguagem (TS/JS), frameworks (React, Next, Express, NestJS…), ORMs (Prisma, Drizzle, Mongoose…), libs (Zod, JWT, Socket.io…) |
| `pyproject.toml` / `requirements.txt` | Python + FastAPI / Django / Flask / SQLAlchemy |
| `go.mod` | Go + Gin / Echo / Fiber |
| `Cargo.toml` | Rust |
| `docker-compose.yml` | Docker Compose |
| `.env.example` | Nomes de todas as variáveis de ambiente |
| `Makefile` | Targets `make` disponíveis |
| `README.md` | Primeiro parágrafo como descrição do projeto |

Seções que não podem ser detectadas automaticamente (`## Depende de`, `## Expõe para`, `## Observações`) ficam em branco para você preencher.

---

## Linguagens suportadas

| Linguagem | Extensões | O que é extraído |
|-----------|----------|-----------------|
| JavaScript | `.js`, `.mjs`, `.cjs` | imports, funções, classes |
| TypeScript | `.ts`, `.tsx` | imports, funções, classes, interfaces |
| JSX | `.jsx` | imports, funções, componentes |
| Python | `.py` | imports, funções, classes (via AST) |

---

## Estrutura da memória do projeto

```
<nome-do-projeto>/
├── graph/
│   └── graph.json          # nós (arquivo/função/classe) + arestas (imports/defines)
├── memory/
│   └── RESUMO.md           # resumo gerado automaticamente, edite livremente
└── logs/
    ├── activity.md         # cada sync registrado aqui
    ├── 2024-01-15.md       # log diário de sessão (criado pelo /salvar-grafo)
    └── 2024-01-16.md
```

### Formato do graph.json

```json
{
  "project": "meu-projeto",
  "stats": { "files": 205, "functions": 102, "classes": 11, "edges": 312 },
  "nodes": [
    { "id": "src_api_users_ts", "label": "users.ts", "type": "file",
      "file": "src/api/users.ts", "group": "api" },
    { "id": "src_api_users_ts__getUser", "label": "getUser", "type": "function",
      "file": "src/api/users.ts", "group": "api" }
  ],
  "edges": [
    { "source": "src_api_users_ts", "target": "src_services_user_ts",
      "relation": "imports" }
  ]
}
```

### Grupos de nós

| Grupo | Diretórios |
|-------|-----------|
| `api` | `api/`, `routes/`, `controllers/` |
| `ui` | `components/`, `pages/`, `views/` |
| `service` | `services/`, `service/` |
| `model` | `models/`, `model/`, `schema/` |
| `hook` | `hooks/` |
| `util` | `utils/`, `helpers/`, `lib/` |
| `config` | `config/`, `settings/`, `env/` |
| `test` | `test/`, `tests/`, `__tests__/`, `spec/` |

---

## Funcionalidades do visualizador

- **Grafo 3D de força** — nós se repelem, câmera orbita livremente (WebGL via three.js)
- **Auto-fit ao carregar** — o grafo sempre fica enquadrado ao trocar de projeto
- **Tamanho por grau** — nós mais conectados aparecem maiores
- **Partículas nas arestas de import** — pontos animados fluem pelas setas de dependência
- **Sidebar com árvore de arquivos** — mesma estrutura de pastas do projeto, funções aninhadas
- **Seletor de projeto** — dropdown suportando projetos ilimitados
- **Painel Memory** — clique em Memory para ler o RESUMO.md do projeto
- **Logs de sessão** — clique em Logs para navegar pelos logs diários
- **Busca** — encontra qualquer função, arquivo ou componente no grafo
- **Painel de detalhes** — clique num nó para ver o que ele importa e o que o usa
- **Exportar PNG** — baixa um screenshot da visão atual
- **Rotação automática** — órbita suave quando ocioso, pausa na interação

---

## Referência de comandos

```bash
# Sincronizar um projeto (criar ou atualizar todos os dados)
python3 ~/Dev/Rag/rag /caminho/para/o/projeto

# Iniciar o visualizador 3D em localhost:7842
python3 ~/Dev/Rag/rag --serve

# Listar todos os projetos sincronizados com stats
python3 ~/Dev/Rag/rag --status
```

| Arquivo | Escrito por | Contém |
|---------|------------|--------|
| `graph/graph.json` | sync (automático) | Grafo do código |
| `memory/RESUMO.md` | sync + você | Resumo do projeto |
| `logs/activity.md` | sync (automático) | Histórico de syncs |
| `logs/AAAA-MM-DD.md` | Claude (`/salvar-grafo`) | Log diário de sessão |
| `projects.json` | sync (automático) | Índice de projetos |

---

## Ignorando arquivos

O scanner ignora estes diretórios por padrão:

```
node_modules  .git  dist  build  .next  __pycache__  coverage
```

---

## Contribuindo

PRs são bem-vindos. O código é intencionalmente simples — sem build step, sem gerenciador de pacotes, sem framework.

```
scripts/sync.py       ~330 linhas  — orquestrador
scripts/graph_gen.py  ~200 linhas  — parser AST
viewer/app.js         ~600 linhas  — visualizador 3D (JS puro)
viewer/style.css      ~400 linhas  — tema dark
serve.py               ~30 linhas  — servidor HTTP local
```

---

## Autor

Feito com foco por **Lucas Amaral** — 🇧🇷 Brasil.

Se isso te economizou tempo, considera um café:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/koalitos)

---

## Licença

MIT
