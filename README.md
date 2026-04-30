# Session-Engram

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Engram**: The physical trace of memory in the brain.
>
> Cross-dialogue session memory system — persistent context, reusable experience, AI automatic recall.

[English](docs/README_EN.md) | [中文](docs/README_CN.md)

---

## What is Session-Engram?

Session-Engram is a **cross-session memory system for AI coding assistants**. It solves two fundamental problems:

1. **Cross-Session Memory Loss** — When a conversation gets too long, starting a new session yields better results. But the new session cannot reuse the previous session's memory.

2. **Experience Doesn't Carry Over** — Effective solutions and lessons learned during programming live only in the current session and are lost when it ends.

## How It Works

Session-Engram stores session memory and experiences as **structured Markdown files**, then uses a **Hook mechanism** to make the AI automatically read them at the start of each new session.

- **Storage layer**: Sessions and Experiences stored as Markdown files — human-readable, AI-readable, Git-trackable
- **Index layer**: `index.md` is a lightweight summary, avoiding stuffing all memory into context (saves tokens)
- **Activation layer**: Hook + rule injection makes AI "passively triggered" rather than "actively remembering"

## Quick Start

```bash
pip install session-engram

# Initialize .engram directory (auto-installs AI platform integration)
sengram init

# Generate memory map (relationship graph)
sengram map

# Generate timeline (log view)
sengram timeline

# Generate memory index (AI entry point)
sengram index
```

## Documentation

- **Full English Documentation**: [README_EN.md](docs/README_EN.md)
- **完整中文文档**: [README_CN.md](docs/README_CN.md)

## License

MIT - See [LICENSE](LICENSE)
