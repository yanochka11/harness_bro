#!/usr/bin/env python3
"""Track tool sequences and capture USEFUL workflow patterns as draft skills.

Filters (defense-in-depth против шума):
1. Whitelist tools: только Read/Write/Edit/Bash/Grep/Glob/WebFetch.
   Игнорируем TaskCreate/TaskUpdate/TaskList/TaskGet/TaskOutput/Skill/ToolSearch
   (это внутренняя механика, не workflow пользователя).
2. Min unique tools в тройке: 3 (отсекает T→T→B, B→B→B).
3. Min sequence repeats: 3 (только устойчивые паттерны, не разовое).
4. Bash content filter: тройка с Bash считается только если хотя бы одна
   bash-команда содержит сигнал (pytest, ruff, mypy, git commit, nvidia-smi,
   python run.py, conda, pip install). Иначе ls/echo/cat — не workflow.

Эффект: 0-2 действительно полезных драфта за сессию вместо 10-20 шума.
"""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

PROJ = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
STATE = PROJ / ".claude/state/tool_trace.jsonl"
AUTO = PROJ / ".claude/skills/auto"
STATE.parent.mkdir(parents=True, exist_ok=True)
AUTO.mkdir(parents=True, exist_ok=True)

# Whitelist реальных рабочих инструментов
USEFUL_TOOLS = {"Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch", "NotebookEdit"}

# Сигналы что bash-команда — это рабочий процесс, не утилита
BASH_SIGNALS = (
    "pytest", "ruff", "mypy", "pyright", "black",
    "git commit", "git push", "git rebase", "git merge",
    "nvidia-smi", "wandb", "huggingface-cli", "hf ",
    "python run", "python -m", "python train", "python eval",
    "conda install", "conda create", "pip install", "uv add", "uv sync",
    "docker", "kubectl",
    "npm install", "npm run",
    "make ", "ninja", "cmake",
)

# Минимальные пороги — ужесточены чтобы фильтровать шум
MIN_REPEATS = 3
MIN_UNIQUE_TOOLS_IN_TRIPLE = 3
MIN_ENTRIES_IN_SESSION = 12

data = json.load(sys.stdin)
event = data.get("hook_event_name", "")
session_id = data.get("session_id", "unknown")

if event == "PostToolUse":
    tool = data.get("tool_name")
    if tool not in USEFUL_TOOLS:
        sys.exit(0)
    entry = {
        "t": time.time(),
        "session": session_id,
        "tool": tool,
        "input_hash": hashlib.md5(
            json.dumps(data.get("tool_input", {}), sort_keys=True).encode()
        ).hexdigest()[:8],
        "input_preview": str(data.get("tool_input", {}))[:200],
    }
    with STATE.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    sys.exit(0)

if event != "Stop" and "--finalize" not in sys.argv:
    sys.exit(0)

if not STATE.exists():
    sys.exit(0)

entries = []
with STATE.open() as f:
    for line in f:
        try:
            e = json.loads(line)
            if e.get("session") == session_id:
                entries.append(e)
        except Exception:
            pass

if len(entries) < MIN_ENTRIES_IN_SESSION:
    sys.exit(0)


def bash_has_signal(preview: str) -> bool:
    low = preview.lower()
    return any(sig in low for sig in BASH_SIGNALS)


def triple_is_meaningful(triple_entries: list[dict]) -> bool:
    tools = [e["tool"] for e in triple_entries]
    if len(set(tools)) < MIN_UNIQUE_TOOLS_IN_TRIPLE:
        return False
    # Если в тройке есть Bash — хотя бы одна Bash-команда должна нести сигнал
    bash_entries = [e for e in triple_entries if e["tool"] == "Bash"]
    if bash_entries and not any(bash_has_signal(e["input_preview"]) for e in bash_entries):
        return False
    return True


# Соберём тройки — но только meaningful
meaningful_triples = []
for i in range(len(entries) - 2):
    triple_entries = entries[i:i + 3]
    if triple_is_meaningful(triple_entries):
        triple_key = tuple(e["tool"] for e in triple_entries)
        meaningful_triples.append((triple_key, triple_entries))

if not meaningful_triples:
    sys.exit(0)

cnt = Counter(t[0] for t in meaningful_triples)

saved = 0
for triple_key, n in cnt.items():
    if n < MIN_REPEATS:
        continue
    slug = "-".join(t.lower() for t in triple_key)
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = AUTO / f"auto-{slug}-{ts}"
    if out_dir.exists():
        continue
    out_dir.mkdir(parents=True)

    examples = [te for tk, te in meaningful_triples if tk == triple_key][:2]
    body_examples = "\n\n".join(
        f"### Example {idx + 1}\n"
        f"- {triple_key[0]}: `{ex[0]['input_preview']}`\n"
        f"- {triple_key[1]}: `{ex[1]['input_preview']}`\n"
        f"- {triple_key[2]}: `{ex[2]['input_preview']}`"
        for idx, ex in enumerate(examples)
    )

    skill = f"""---
name: auto-{slug}-{ts}
description: Auto-captured workflow {triple_key[0]}->{triple_key[1]}->{triple_key[2]} (seen {n}x). Review and rename to promote.
auto-generated: true
draft: true
---

# Auto-captured: {' -> '.join(triple_key)}

Pattern observed {n} times in session `{session_id}`.

## Observed examples
{body_examples}

## Promote
1. Rename directory to meaningful name
2. Set `draft: false`, remove `auto-generated`
3. Refine description (use 'Use when ...' triggers)
4. Move to `skills/curated/<bucket>/`

## Discard
`rm -rf` this directory if not useful (or wait for cleanup.sh).
"""
    (out_dir / "SKILL.md").write_text(skill)
    saved += 1

if saved:
    print(f"[auto-save] {saved} draft skill(s) saved to {AUTO}", file=sys.stderr)

sys.exit(0)
