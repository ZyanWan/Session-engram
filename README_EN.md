# Session-Engram

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Engram**: The physical trace of memory in the brain.
>
> Cross-dialogue session memory system — persistent context, reusable experience, AI automatic recall.

[English](README_EN.md) | [中文](README_CN.md)

## Background: The Memory Problem in AI-Assisted Programming

AI coding assistants (Claude Code, OpenCode, Cursor, etc.) face two fundamental problems in practice:

### Problem 1: Cross-Session Memory Loss

When a conversation gets too long, starting a new session yields better results. But the new session **cannot reuse the previous session's memory** — the AI doesn't know what was already done, forcing the user to re-explain context. This is especially painful for related tasks:

> User: "Continue working on the frontend page"
> AI: "Where did you leave off?" (Has no idea the previous session already completed 80%)

![Cross-Session Memory Loss](pictures/memory-gap-session-loss.png)

### Problem 2: Experience Doesn't Carry Over

During programming, both AI and users encounter typical task patterns, unexpected pitfalls, and effective solutions. These **live only in the current session** and are lost when it ends:

> Last session hit a SearchReplace batch replace bug, spent 20 minutes debugging.
> Next time the same issue comes up, the AI starts from scratch.

### The Solution

Session-Engram's approach: **store session memory and experiences as structured files, then use a Hook mechanism to make the AI automatically read them at the start of each new session.**

![Structured Storage Architecture](pictures/structured-storage-architecture.png)

```
┌──────────────────────────────────────────────────────────────┐
│  Session ends                                                 │
│  ├── sengram index → writes lightweight summary to             │
│  │   .engram/index.md                                         │
│  └── Experience files written to .engram/experience/           │
│                                                                │
│  New session starts                                            │
│  ├── Hook fires → reminds AI to read .engram/index.md          │
│  ├── AI learns: active tasks, history, reusable experiences     │
│  └── AI decides whether to deep-read specific files             │
└──────────────────────────────────────────────────────────────┘
```

Core design principles:

- **Storage layer**: Sessions and Experiences stored as Markdown files — human-readable, AI-readable, Git-trackable
- **Index layer**: `index.md` is a lightweight summary, avoiding stuffing all memory into context (saves tokens)
- **Activation layer**: Hook + rule injection makes AI "passively triggered" rather than "actively remembering" — AI won't check memory on its own, it must be reminded

## Installation

```bash
pip install session-engram
```

Or from source:

```bash
git clone https://github.com/YOUR_USERNAME/session-engram.git
cd session-engram
pip install -e .
```

## Quick Start

```bash
# Initialize .engram directory (auto-installs AI platform integration)
sengram init

# Check status
sengram info

# Generate memory map (relationship graph)
sengram map

# Generate timeline (log view)
sengram timeline

# Generate memory index (AI entry point)
sengram index

# Manual install/uninstall AI platform integration
sengram install claude      # Claude Code
sengram install opencode    # OpenCode
sengram install agents      # Generic platform (AGENTS.md)
sengram uninstall claude    # Uninstall Claude integration

# List all engrams
sengram list

# Archive old sessions
sengram archive
```

## How It Works

### Directory Structure

Session-Engram stores memory in `.engram/` directory:

```
.engram/
├── index.md              # Lightweight summary index (AI reads this)
├── engram-map.html       # Interactive relationship graph
├── engram-timeline.html  # Timeline log view
├── session/              # Cross-dialogue sessions
│   ├── session-*.md      # Full record of each session
│   └── archive/          # Archived sessions
└── experience/           # Reusable knowledge (project-level)
    ├── design/           # Design experiences
    ├── technical/        # Technical experiences
    └── business/         # Business experiences
```

Global experience library is stored in the user's home directory, shared across projects:

```
~/.sengram/
└── experience/           # Cross-project global experience library
    ├── design/
    ├── technical/
    └── business/
```

### Two Memory Types

| Type | Purpose | Example |
|------|---------|---------|
| **Session** | Track ongoing work across conversations | "Building auth system, step 3 of 5" |
| **Experience** | Store reusable solutions and lessons | "JWT refresh token pattern", "SearchReplace batch replace gotcha" |

### Data Flow

```
Session in progress
    ↓
User/AI summarizes → session-*.md (status, tags, summary, progress)
    ↓
Encounters typical problem → experience/*.md (problem, solution, lesson)
    ↓
Session ends → sengram index → .engram/index.md updated
    ↓
New session starts → Hook fires → AI reads index.md → inherits memory
```

### Core Architecture

```
session_engram/
├── cli.py                     # CLI entry point, command registry
├── core/                      # Core modules
│   ├── config.py              # Constants (paths, categories, archive policy)
│   ├── storage.py             # Directory management (get_memory_root, ensure_dirs)
│   ├── parser.py              # Markdown parsing (front matter, summary extraction)
│   ├── scanner.py             # File scanning (traverse all engram files)
│   ├── graph.py               # Graph data builder (nodes, edges, communities, tag groups)
│   ├── visualizer.py          # vis.js relationship graph HTML generation
│   ├── timeline.py            # Timeline data builder
│   ├── timeline_visualizer.py # Timeline HTML generation
│   └── indexer.py             # Memory index generator (index.md)
├── commands/                  # CLI command implementations
│   ├── init.py                # sengram init
│   ├── info.py                # sengram info
│   ├── map.py                 # sengram map
│   ├── timeline.py            # sengram timeline
│   ├── index.py               # sengram index
│   ├── install.py             # sengram install / uninstall
│   ├── export.py              # sengram export
│   ├── list.py                # sengram list
│   ├── check.py               # sengram check
│   ├── update.py              # sengram update
│   └── archive.py             # sengram archive
├── templates/                 # HTML / Markdown templates
│   ├── engram-map.html        # Relationship graph page template
│   ├── engram-timeline.html   # Timeline page template
│   ├── session-template.md    # Session template
│   ├── experience-template.md # Experience template
│   └── index-template.md      # Index template
└── tests/                     # Test suite
```

#### Core Modules in Detail

| Module | Responsibility |
|--------|----------------|
| `config.py` | Defines directory paths, experience categories (design/technical/business), archive policy (7 days), date format, global experience library path (`~/.sengram/experience`) |
| `storage.py` | Provides `get_memory_root()` and `ensure_dirs()` to auto-create the `.engram/` and `~/.sengram/` directory structures |
| `parser.py` | Parses YAML Front Matter from Markdown files, extracting status, tags, timestamps; extracts summary from body text |
| `scanner.py` | Traverses all files under `.engram/`, returning complete metadata lists for sessions, experiences, and archives |
| `graph.py` | **Graph engine**: Builds session/experience into a graph structure — nodes are files, edges are shared-tag relationships, communities clustered by type |
| `visualizer.py` | Generates interactive vis.js relationship maps with community coloring, edge weights, hyperedges, and performance warnings |
| `timeline.py` | Builds chronological timeline data sorted by creation time |
| `timeline_visualizer.py` | Generates standalone HTML timeline pages with month grouping, type filtering, and expandable detail cards |
| `indexer.py` | **Core**: Scans project-level `.engram/` and user-level `~/.sengram/` to generate `index.md` — a lightweight AI-readable summary |

#### Graph Building Logic

`graph.py` implements a tag-based knowledge graph:

- **Nodes**: One node per session/experience file, extracting status, tags, timestamps, and summary from front matter
- **Edges**: Created when two nodes share at least one tag; `weight` equals the number of shared tags
- **Relation types**:
  - `shares_tag`: Between same-type nodes (session-session or experience-experience)
  - `inspired`: Between session and experience (shown as dashed arrows)
- **Communities**: 6 categories by file_type — active/completed/archived sessions, design/technical/business experiences

## Commands

| Command | Description |
|---------|-------------|
| `sengram init` | Initialize `.engram/` directory structure, **auto-install AI platform integration** |
| `sengram info` | Show status and directory info |
| `sengram map` | Generate interactive relationship graph (vis.js) |

![Knowledge Graph](pictures/knowledge-graph-constellation-map.png)

| `sengram timeline` | Generate timeline log view |

![Timeline](pictures/chronological-timeline-view.png)

| `sengram index` | Generate AI-readable memory index (`index.md`) |
| `sengram update` | Update `index.md` in table format (human-readable version) |
| `sengram install` | Install AI platform integration (Hook + rules) |
| `sengram uninstall` | Remove AI platform integration (precise uninstall, doesn't affect other platforms) |
| `sengram list` | List all engrams |
| `sengram check` | Check status, suggest archivable sessions |
| `sengram export` | Export memory data (JSON / GraphML) |
| `sengram archive` | Archive inactive sessions (7 days without activity) |

## AI Integration

Session-Engram uses a **Hook mechanism** to make AI actively read memory, rather than waiting for user prompts.

![Hook Mechanism](pictures/hook-mechanism-context-inheritance.png)

### Why Hooks?

AI won't check memory files on its own — even if rules are written in `CLAUDE.md`, AI often "forgets" to look during long conversations. Hooks **force a reminder** at key moments (e.g., before tool calls or file reads), ensuring AI never skips memory retrieval.

This is inspired by [graphify](https://github.com/safishamsi/graphify)'s PreToolUse Hook pattern: injecting context hints before AI executes tool calls.

### Auto-Install (sengram init)

Starting from v1.0.0, `sengram init` **automatically detects and installs AI platform integration**:

- Detects `.claude/` directory → auto-installs Claude Code integration (`CLAUDE.md` + PreToolUse Hook)
- Detects `.opencode/` directory → auto-installs OpenCode integration (`AGENTS.md` + plugin)
- Otherwise → installs generic integration (`AGENTS.md`)

No need to manually run `sengram install` — AI knows about the memory system from project initialization.

### Manual Install

```bash
sengram install claude      # Writes CLAUDE.md + PreToolUse hook
sengram install opencode    # Writes AGENTS.md + plugin
sengram install agents      # Writes AGENTS.md (rules only)
sengram install             # Auto-detect platform
```

### Uninstall

```bash
sengram uninstall claude    # Removes only CLAUDE.md and .claude/settings.json
sengram uninstall opencode  # Removes only AGENTS.md and .opencode/plugins/
sengram uninstall agents    # Removes only AGENTS.md
```

**Platform rule files are isolated**. Uninstalling Claude won't delete AGENTS.md, and uninstalling OpenCode won't delete CLAUDE.md.

### How It Works

**Hook interception**: When AI executes Bash or Read tools, the hook detects `.engram/index.md` and injects a reminder:

> "This project has a memory system. Read .engram/index.md for session history and reusable experiences."

**Rule injection**: `CLAUDE.md` / `AGENTS.md` gets always-on rules telling AI to:
- Read `.engram/index.md` at every session start
- Check history when working on related tasks
- Look for reusable experiences in `experience/`
- **If index.md shows a freshness warning ("Index stale"), run `sengram index` immediately**
- **When reading an experience file, increment its `uses` counter in front matter if it helped solve the current problem**
- Run `sengram index` after completing a task

### Platform Support

| Platform | Rules File | Hook |
|----------|-----------|------|
| Claude Code | `CLAUDE.md` | `.claude/settings.json` PreToolUse (Bash + Read) |
| OpenCode | `AGENTS.md` | `.opencode/plugins/sengram.js` |
| Other | `AGENTS.md` | None (rules only) |

## index.md Smart Features

`index.md` is not just a static index — it includes the following intelligent hints:

### Freshness Detection

If source files under `.engram/` are newer than `index.md`, a warning appears at the top:

```markdown
> ⚠️  **Index stale (session/auth.md is newer) — run `sengram index`**
```

AI will immediately know an update is needed, avoiding stale memory.

### Quick Context Hint

The top of index.md shows a statistical summary of the current memory library:

```markdown
> 💡 2 active session(s) | 14 experience(s) | 3 global experience(s)
```

### Experience Usage Counter

Experience files support a `uses` field (in front matter) to track how many times AI read and found it helpful:

```markdown
---
type: experience
uses: 3
tags: [git, rebase]
---
```

index.md sorts by usage frequency, prioritizing high-frequency experiences:

```markdown
- [git-rebase-best-practice](...) `git, rebase` (used 3×)
```

### Global Experience Library

Cross-project general experiences are stored in `~/.sengram/experience/`, also categorized by design/technical/business. `sengram index` automatically scans and displays them in a separate section:

```markdown
## Global Experiences (Cross-Project)

### Technical (2)
- [git-rebase-best-practice](...) `git, rebase` (used 3×)
```

AI can read global experiences in any project, enabling true cross-project knowledge reuse.

## Data Format

### Session Template

```markdown
---
type: session
status: in-progress
created: 2026-04-30 10:00
updated: 2026-04-30 10:00
tags: [auth, jwt, backend]
summary: |
  ## Task Goal
  Build user authentication system

  ## Current Progress
  Login API completed

  ## Next Steps
  Implement refresh token mechanism
---

# session-auth-system

## Background
...
```

### Experience Template

```markdown
---
type: experience
status: resolved
created: 2026-04-30 10:00
updated: 2026-04-30 10:00
tags: [jwt, security, bugfix]
uses: 0
summary: |
  ## Problem
  Refresh token race condition under concurrent requests

  ## Solution
  Use Redis lock + dual-write strategy

  ## Conclusion
  See experience/jwt-refresh-token.md
---

# exp-jwt-refresh-token

## Symptoms
...
```

## License

MIT - See [LICENSE](LICENSE)
