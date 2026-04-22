# RAG — Local Code Intelligence for Claude

> A self-hosted knowledge graph that gives Claude persistent memory about your codebases — with a 3D interactive graph viewer.

![RAG Viewer](https://img.shields.io/badge/viewer-3D_graph-58a6ff?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9+-3fb950?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-bc8cff?style=flat-square)
![No cloud](https://img.shields.io/badge/cloud-none-ff9f1a?style=flat-square)
![Made in Brazil](https://img.shields.io/badge/made%20in-Brazil%20🇧🇷-009c3b?style=flat-square)

---

## The problem

Every time you open a new Claude Code session, it starts from zero. You explain the stack again. You re-describe the architecture. You paste the same file paths over and over. Claude is smart, but it has no memory — and that constant re-explanation wastes time and breaks flow.

The usual fix is to dump everything into `CLAUDE.md`. But that gets messy fast: no structure, no automation, outdated the moment the code changes, and you're still writing it by hand.

---

## The idea

What if Claude always knew your project — the files, the functions, the dependencies, the decisions you made last week — without you having to explain it again?

That's what RAG does. It's a **local knowledge graph** that sits alongside your projects:

- Scans your codebase and builds a structured map of files, functions, classes and imports
- Auto-detects your stack (Node.js, Python, Go, Rust, Docker…) and writes a project summary
- Keeps session logs — what Claude worked on each day, what was decided, what's next
- Injects context into `CLAUDE.md` so Claude reads the graph before answering **anything**
- Serves a **3D interactive graph viewer** — orbit, zoom, click nodes, see connections live

Everything runs locally. No API calls, no cloud, no subscriptions.

---

## How it was built

The goal was to keep it as simple as possible — no frameworks, no build step, no package manager. Just Python and vanilla JS.

The sync script (`scripts/sync.py`) reads your project files using Python's `ast` module for Python code and regex for JS/TS. It walks the directory tree, extracts nodes (files, functions, classes) and edges (imports, definitions), then writes a `graph.json`. It also sniffs your config files — `package.json`, `pyproject.toml`, `go.mod`, `.env.example` — and auto-generates a `RESUMO.md` with stack, scripts and env vars already filled in.

The viewer (`viewer/app.js`) uses [3d-force-graph](https://github.com/vasturiano/3d-force-graph) — a WebGL force-directed graph — to render the code as a living 3D atom you can orbit and explore. Nodes are sized by how many connections they have. Import edges have animated particles flowing through them. Click a node and a details panel slides in showing everything it imports and everything that uses it.

The `CLAUDE.md` injection forces Claude to print a formatted context block at the start of every session — stack, file count, last sync time, project summary — before answering anything.

---

## Demo

```
┌─ RAG Viewer (localhost:7842) ──────────────────────────────────────┐
│                                                                      │
│  [Explorer]        [  ●  3D force graph — orbit with mouse  ●  ]   │
│  ▼ src                                                               │
│    ▼ api           Nodes glow by group: api · service · model       │
│      users.ts  5   Particles flow along import edges                │
│        ƒ getUser   Click any node → details panel slides in         │
│        ƒ create                                                      │
│    ▶ services   [ Logs ]  ── daily session log viewer ──            │
│    ▶ models     [ Memory ] ── project RESUMO.md ──                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## How it works

```
~/Dev/Rag/                     ← this repo
│
├── scripts/
│   ├── sync.py                ← scans a project and writes RAG data
│   └── graph_gen.py           ← AST parser (JS/TS/Python)
│
├── viewer/                    ← 3D graph viewer (served via HTTP)
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── projects.json              ← index of all synced projects
│
└── <project-name>/            ← one folder per project
    ├── graph/graph.json       ← code graph (auto-generated)
    ├── memory/RESUMO.md       ← project summary (auto-generated + editable)
    └── logs/
        ├── activity.md        ← sync history
        └── 2024-01-15.md      ← daily session log

~/Dev/my-project/              ← your real project (untouched)
    └── CLAUDE.md              ← RAG instructions injected here
```

Your real projects are **never modified** except for `CLAUDE.md`.

---

## Quick start

### 1. Clone this repo

```bash
git clone https://github.com/your-username/rag ~/Dev/Rag
```

No dependencies to install — just Python 3.9+ (standard library only).

### 2. Sync a project

```bash
python3 ~/Dev/Rag/rag /path/to/my-project
```

This will:
- Parse all `.js`, `.ts`, `.jsx`, `.tsx`, `.py` files and generate a code graph
- Auto-detect the stack from `package.json`, `pyproject.toml`, `go.mod`, etc.
- Create `<project>/memory/RESUMO.md` pre-filled with stack, scripts, env vars and structure
- Write a `CLAUDE.md` in your project forcing Claude to load the RAG context every session
- Create a daily log at `<project>/logs/YYYY-MM-DD.md`

### 3. Start the viewer

```bash
python3 ~/Dev/Rag/rag --serve
```

Opens `http://localhost:7842` automatically. The 3D graph is interactive:
- **Drag** to orbit, **scroll** to zoom
- **Click** a node to see its connections in the details panel
- **Hover** for a tooltip with name, type and file path
- **Sidebar** shows the real folder tree with functions nested under files
- **Memory** button shows the project RESUMO.md inline
- **Logs** button shows daily session logs

### 4. Check status

```bash
python3 ~/Dev/Rag/rag --status
```

---

## Claude Code integration

After syncing, your project's `CLAUDE.md` will contain:

```markdown
## RAG — Required context

ABSOLUTE RULE: at the start of every session, BEFORE answering anything, you MUST:

1. Read the files listed below in order
2. Print a context block:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RAG loaded: my-project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Stack:      Node.js + TypeScript, NestJS, Prisma
  Files:      205 files · 102 functions · 198 classes
  Last sync:  2024-01-15 14:32
  Summary:    REST API for user authentication...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Claude reads the graph, memory and logs **before every response** — so it always knows the project without you re-explaining it.

### Claude Code skills (optional)

Add these to your global `~/.claude/CLAUDE.md` for slash command shortcuts:

**`/salvar-grafo`** — re-sync the graph and append a session summary to today's log:
```markdown
# salvar-grafo
When the user types `/salvar-grafo`, run sync.py for the current project and
append a session block to logs/YYYY-MM-DD.md with what was done this session.
```

**`/retomar-grafo`** — load full project context at session start:
```markdown
# retomar-grafo
When the user types `/retomar-grafo`, read the RAG memory, recent daily log
and graph stats, then print a formatted context summary.
```

---

## Auto-detected stack

`sync.py` reads your project files and fills in `memory/RESUMO.md` automatically:

| File | What's detected |
|------|----------------|
| `package.json` | Runtime (Node/Bun), language (TS/JS), frameworks (React, Next, Express, NestJS…), ORMs (Prisma, Drizzle, Mongoose…), libraries (Zod, JWT, Socket.io…) |
| `pyproject.toml` / `requirements.txt` | Python + FastAPI / Django / Flask / SQLAlchemy |
| `go.mod` | Go + Gin / Echo / Fiber |
| `Cargo.toml` | Rust |
| `docker-compose.yml` | Docker Compose |
| `.env.example` | All environment variable names |
| `Makefile` | Available `make` targets |
| `README.md` | First paragraph as project description |

Sections that can't be auto-detected (`## Depende de`, `## Expõe para`, `## Observações`) are left blank for you to fill in.

---

## Supported languages

| Language | Extensions | What's extracted |
|----------|-----------|-----------------|
| JavaScript | `.js`, `.mjs`, `.cjs` | imports, functions, classes |
| TypeScript | `.ts`, `.tsx` | imports, functions, classes, interfaces |
| JSX | `.jsx` | imports, functions, components |
| Python | `.py` | imports, functions, classes (via AST) |

---

## Project memory structure

```
<project-name>/
├── graph/
│   └── graph.json          # nodes (file/function/class) + edges (imports/defines)
├── memory/
│   └── RESUMO.md           # auto-generated summary, edit freely
└── logs/
    ├── activity.md         # every sync logged here
    ├── 2024-01-15.md       # daily session log (created by /salvar-grafo)
    └── 2024-01-16.md
```

### graph.json format

```json
{
  "project": "my-project",
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

### Node groups

| Group | Directories |
|-------|-------------|
| `api` | `api/`, `routes/`, `controllers/` |
| `ui` | `components/`, `pages/`, `views/` |
| `service` | `services/`, `service/` |
| `model` | `models/`, `model/`, `schema/` |
| `hook` | `hooks/` |
| `util` | `utils/`, `helpers/`, `lib/` |
| `config` | `config/`, `settings/`, `env/` |
| `test` | `test/`, `tests/`, `__tests__/`, `spec/` |

---

## Viewer features

- **3D force graph** — nodes repel each other, camera orbits freely (WebGL via three.js)
- **Auto-fit on load** — graph is always framed when switching projects
- **Size by degree** — heavily connected nodes appear larger
- **Particles on import edges** — animated dots flow along dependency arrows
- **File tree sidebar** — same folder structure as your project, functions nested under files
- **Project picker** — dropdown supporting unlimited projects
- **Memory panel** — click Memory to read the project RESUMO.md inline
- **Session log viewer** — click Logs to browse daily session logs
- **Search** — finds any function, file or component across the graph
- **Details panel** — click any node to see what it imports and what uses it
- **PNG export** — downloads a screenshot of the current view
- **Auto-rotation** — gentle orbit when idle, pauses on interaction

---

## Command reference

```bash
# Sync a project (create or update all RAG data)
python3 ~/Dev/Rag/rag /path/to/project

# Start the 3D viewer at localhost:7842
python3 ~/Dev/Rag/rag --serve

# List all synced projects with stats
python3 ~/Dev/Rag/rag --status
```

| File | Written by | Contains |
|------|-----------|---------|
| `graph/graph.json` | sync (automatic) | Code graph |
| `memory/RESUMO.md` | sync + you | Project summary |
| `logs/activity.md` | sync (automatic) | Sync history |
| `logs/YYYY-MM-DD.md` | Claude (`/salvar-grafo`) | Daily session log |
| `projects.json` | sync (automatic) | Project index |

---

## Ignoring files

The scanner ignores these directories by default:

```
node_modules  .git  dist  build  .next  __pycache__  coverage
```

---

## Contributing

PRs welcome. The codebase is intentionally simple — no build step, no package manager, no framework.

```
scripts/sync.py       ~330 lines  — orchestrator
scripts/graph_gen.py  ~200 lines  — AST parser
viewer/app.js         ~600 lines  — 3D viewer (vanilla JS)
viewer/style.css      ~400 lines  — dark theme
serve.py               ~30 lines  — local HTTP server
```

---

## Author

Made with focus by **Lucas Amaral** — 🇧🇷 Brazil.

If this saved you time, consider buying a coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/koalitos)

---

## License

MIT
