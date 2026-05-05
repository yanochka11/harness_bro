#!/usr/bin/env python3
"""After Claude writes/edits a .py file, validate in three steps.

1. AST parse        — синтаксис.
2. py_compile       — bytecode-компиляция (ловит чуть больше edge cases чем ast).
3. ruff F-rules     — реальные баги имён: undefined name (F821),
                       local-before-assignment (F823), redefinition (F811).
                       Без auto-fix.

Если что-то падает — возвращаем decision=block с конкретной строкой/правилом,
Claude видит сообщение и фиксит сам.
"""
import ast
import json
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


data = json.load(sys.stdin)
if data.get("hook_event_name") != "PostToolUse":
    sys.exit(0)
if data.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

inp = data.get("tool_input", {})
path = inp.get("file_path") or inp.get("path", "")
if not path.endswith(".py"):
    sys.exit(0)

p = Path(path)
if not p.is_file():
    sys.exit(0)

try:
    src = p.read_text()
except Exception:
    sys.exit(0)

try:
    ast.parse(src)
except SyntaxError as e:
    block(f"Python AST error in {path}:{e.lineno}: {e.msg}. Fix the syntax and try again.")

try:
    py_compile.compile(path, doraise=True)
except py_compile.PyCompileError as e:
    block(f"py_compile failed: {e}")

ruff = shutil.which("ruff")
if ruff:
    try:
        out = subprocess.run(
            [
                ruff,
                "check",
                "--select=F821,F823,F811",
                "--no-fix",
                "--output-format=concise",
                "--force-exclude",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 1 and out.stdout.strip():
            issues = "\n".join(out.stdout.strip().splitlines()[:5])
            block(
                f"ruff found name-resolution bugs in {path}:\n{issues}\n"
                "(F821 undefined name, F823 local-before-assignment, F811 redefinition). "
                "Fix and try again."
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

sys.exit(0)
