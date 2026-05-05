#!/usr/bin/env python3
"""Block writes to user-defined banned paths (read-only quotas, NFS, etc).

Banned paths configured via environment variable HARNESS_BANNED_PATHS
(comma-separated). Empty value = hook does nothing (default for fresh install).

Examples (set in your shell or in .claude/.envrc-like loader):
    export HARNESS_BANNED_PATHS="/home/jovyan,/mnt/readonly"
"""
import json
import os
import re
import sys

raw = os.environ.get("HARNESS_BANNED_PATHS", "").strip()
if not raw:
    sys.exit(0)

patterns = [re.compile(re.escape(p.strip()) + r"(/|$|\b)") for p in raw.split(",") if p.strip()]
if not patterns:
    sys.exit(0)


def matches(text: str) -> str | None:
    for p in patterns:
        if p.search(text):
            return p.pattern.replace("\\", "")
    return None


def block(reason: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"banned-path guard: {reason}. Use a writeable path instead.",
    }))
    sys.exit(0)


data = json.load(sys.stdin)
event = data.get("hook_event_name", "")

if event == "UserPromptSubmit":
    hit = matches(data.get("prompt", ""))
    if hit:
        block(f"prompt mentions banned path ({hit})")

elif event == "PreToolUse":
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {})
    if tool in ("Write", "Edit"):
        path = inp.get("file_path", "") or inp.get("path", "")
        hit = matches(path)
        if hit:
            block(f"writing to banned path {path}")
    elif tool == "Bash":
        cmd = inp.get("command", "")
        hit = matches(cmd)
        if hit and any(v in cmd for v in ("> ", ">>", "rm ", "mv ", "cp ", "mkdir ", "touch ", "tee ")):
            block(f"bash writes to banned path: {cmd[:120]}")

sys.exit(0)
