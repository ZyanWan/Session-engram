---
name: session-engram
version: 1.0.0
description: |
  Cross-dialogue session memory system - Engram for AI context persistence.

  **Trigger Scenarios (Must Use This Skill):**
  - Explicit: User says "engram", "session-engram", "save session", "continue last", "check experience", "memory map"
  - Implicit: User says "continue last work", "how did we solve this", "summarize this conversation"
  - Scenario Detection: Long conversation needs handoff, recurring problems, user requests recording

  **Core Value**: Give AI persistent memory across conversations through local file system.
---

# Session-Engram

Cross-dialogue session memory system. AI achieves context persistence by reading/writing `.engram/` folder.

> **Command**: `sengram <command>`
> **Core**: Session (cross-dialogue context) + Experience (reusable knowledge)

---

## Quick Decision

```
User Intent?
├── Read
│   ├── "Continue last" → Find in-progress session
│   ├── "Check experience" → Match by tags
│   └── "View map" → Generate mind map
└── Write
    ├── Task progress → session template
    └── Solution → experience template
```

---

## Core Concepts

| Type | Purpose | Location |
|------|---------|----------|
| **session** | Cross-dialogue context transfer | `.engram/session/` |
| **experience** | Reusable knowledge base | `.engram/experience/{category}/` |

---

## Folder Structure

```
.engram/
├── index.md              # Global index
├── engram-map.html       # Interactive visualization
├── session/              # Session memory
│   ├── session-*.md
│   └── archive/
└── experience/           # Experience memory
    ├── design/
    ├── technical/
    └── business/
```

---

## CLI Commands

```bash
sengram info      # Show status and directory info
sengram map       # Generate interactive memory map
sengram update    # Rebuild index.md
sengram list      # List all engrams
sengram check     # Check status
sengram archive   # Archive inactive sessions
```

> **Note:** First run will auto-create `.engram/` directory.

---

## Writing Rules

### Trigger Conditions

| Type | What Users Say |
|------|----------------|
| Explicit | "Save session", "Note this", "Write experience" |
| Implicit | Solving difficult problems, "Finally got it" |
| Warning | Conversation > 20 turns, user says "too long" |

### Confirmation (Mandatory)

```
Detect worth-recording content
        ↓
Confirm: "Save this [experience/progress]?"
(Filename + one-line summary)
        ↓
Wait for response → Write if agreed
```

**Must confirm unless user says "save directly".**

---

## Reading Rules

| User Says | Action |
|-----------|--------|
| "Continue last work" | Find latest in-progress session |
| "Check experience" | Match by tags |
| "Show map" | Generate mind map |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/session-template.md` | Session template |
| `templates/experience-template.md` | Experience template |
| `templates/index-template.md` | Index template |

---

## Error Handling

| Scenario | Action |
|----------|--------|
| `.engram/` missing | Auto-created on first run |
| Multiple sessions | Show list for user choice |
| Experience not found | Clearly state, don't fabricate |
| User declines | Don't write, don't ask again |

---

## Key Rules

1. **Confirm first**: Always confirm before writing
2. **Update index**: Must update after read/write
3. **Accurate tags**: Cover task, tech, module
4. **Actionable**: Include commands/paths in conclusions
5. **No pronouns**: Use specific nouns
6. **No guessing**: State clearly if not found
