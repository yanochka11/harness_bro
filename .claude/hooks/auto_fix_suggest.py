#!/usr/bin/env python3
"""Auto-fix loop: после провала pytest/ruff/mypy/pyright подсказывает Claude'у
рецепт из .claude/memory/recipes/.

Срабатывает: PostToolUse(Bash).
Не блокирует — печатает подсказку в stderr, Claude её видит и решает применять.

Логика:
1. Команда содержит pytest|ruff|mypy|pyright.
2. tool_response (stdout+stderr) содержит признак ошибки.
3. Сканируем все .claude/memory/recipes/*.md frontmatter `pattern:`.
4. Если pattern (regex) matches output — печатаем тело рецепта.

Pattern field в recipe — это regex для re.search по выводу команды.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJ_ENV = "CLAUDE_PROJECT_DIR"
import os

PROJ = Path(os.environ.get(PROJ_ENV, "."))
RECIPES_DIR = PROJ / ".claude/memory/recipes"

TRIGGER_TOOLS = ("pytest", "ruff", "mypy", "pyright", "ast-grep")
ERROR_MARKERS = (
    "Error", "error:", "ERROR",
    "FAILED", "failed", "FAIL ",
    "Traceback",
    "AssertionError", "ImportError", "NameError", "TypeError",
    "AttributeError", "KeyError", "ValueError", "IndexError",
    "ModuleNotFoundError", "SyntaxError",
    " F821", " F823", " F811", " E9",
)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm_block = text[4:end]
    body = text[end + 5 :]
    fm: dict[str, str] = {}
    for line in fm_block.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("hook_event_name") != "PostToolUse":
        sys.exit(0)
    if data.get("tool_name") != "Bash":
        sys.exit(0)

    inp = data.get("tool_input", {})
    cmd = inp.get("command", "")
    if not any(t in cmd for t in TRIGGER_TOOLS):
        sys.exit(0)

    # Берём output — может быть строкой или dict с stdout/stderr/output
    response = data.get("tool_response", "") or data.get("tool_output", "")
    if isinstance(response, dict):
        out_text = (response.get("stdout") or "") + "\n" + (response.get("stderr") or "")
    else:
        out_text = str(response)

    if not any(m in out_text for m in ERROR_MARKERS):
        sys.exit(0)

    if not RECIPES_DIR.is_dir():
        sys.exit(0)

    suggestions: list[tuple[str, str, str]] = []
    for recipe_path in sorted(RECIPES_DIR.glob("*.md")):
        try:
            text = recipe_path.read_text()
        except Exception:
            continue
        fm, body = parse_frontmatter(text)
        if fm.get("type") != "recipe":
            continue
        pattern = fm.get("pattern")
        if not pattern:
            continue
        try:
            if re.search(pattern, out_text):
                suggestions.append((fm.get("name", recipe_path.stem), fm.get("description", ""), body.strip()))
        except re.error:
            continue

    if not suggestions:
        sys.exit(0)

    # Печатаем в stderr — Claude видит как часть tool output
    print("", file=sys.stderr)
    print("[auto_fix_suggest] нашёл подходящий recipe(s) в .claude/memory/recipes/:", file=sys.stderr)
    for name, desc, body in suggestions[:3]:
        print(f"\n── {name} ──", file=sys.stderr)
        if desc:
            print(desc, file=sys.stderr)
        print(body[:800], file=sys.stderr)
    print("\n(Если рецепт подошёл — применить. Если нет — ошибка новая, после фикса можно сохранить через skill `record-recipe`.)", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
