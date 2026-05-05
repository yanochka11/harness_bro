#!/usr/bin/env python3
"""Block accidental secret leaks at the Claude Code level.

Triggers (PreToolUse):
- Bash with `git commit`, `git push`, `git add` — scan staged diff via gitleaks (если есть)
  + regex-fallback по списку известных секретов.
- Write/Edit — scan новый/изменённый контент на known secret patterns.

Returns decision=block с подсказкой использовать env vars / .env / secret manager.
False positives минимизированы:
- placeholder'ы (your_*_here, EXAMPLE, xxx, <…>) пропускаются,
- # noqa: secret / # pragma: allowlist secret — disable-comment,
- public keys (*.pub, BEGIN PUBLIC KEY) — пропускаются.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

# ─── Regex-каталог ────────────────────────────────────────────────────
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI (project)", re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}")),
    ("OpenAI (legacy)",  re.compile(r"\bsk-[A-Za-z0-9]{48}\b")),
    ("Anthropic",        re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("HuggingFace",      re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("GitHub PAT",       re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("GitHub OAuth",     re.compile(r"\bgh[ousr]_[A-Za-z0-9]{36}\b")),
    ("AWS access key",   re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key",   re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token",      re.compile(r"xox[abprs]-[0-9A-Za-z-]{10,}")),
    ("Stripe live",      re.compile(r"\b(sk|pk)_live_[0-9a-zA-Z]{24,}\b")),
    ("PEM private key",  re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("JWT",              re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]

# Контекстуальные паттерны (требуют ключевого слова рядом)
CONTEXT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "AWS secret access key",
        re.compile(r"aws_secret_access_key[\"'\s:=]{1,5}[A-Za-z0-9/+=]{40}", re.IGNORECASE),
    ),
    (
        "DB connection string",
        re.compile(r"(?:postgres|postgresql|mysql|mongodb)://[^:\s/@]+:[^@\s]{3,}@", re.IGNORECASE),
    ),
    (
        "WANDB_API_KEY",
        re.compile(r"WANDB_API_KEY[\"'\s:=]{1,5}[a-f0-9]{40}\b"),
    ),
]

# Маркеры false-positive
PLACEHOLDER_HINTS = (
    "your_", "<your", "<api", "<token", "example", "placeholder",
    "xxx", "yyy", "zzz", "redacted", "fake", "dummy", "sample",
    "test_key", "test-key", "test_token",
)
DISABLE_COMMENT = re.compile(r"#\s*(noqa:\s*secret|pragma:\s*allowlist[\s_-]?secret)", re.IGNORECASE)

# Пути которые игнорируем (тестовые fixtures, документация с примерами)
IGNORE_PATH_HINTS = (
    "/tests/fixtures/",
    "/test_data/",
    ".claude/skills/",      # сами skill'ы могут содержать примеры паттернов
    ".claude/hooks/secret_guard.py",  # этот файл
    "/.claude/plugins/marketplaces/",
)


def is_placeholder(line: str, match: str) -> bool:
    low_match = match.lower()
    # match явно содержит placeholder-маркер
    if any(h in low_match for h in PLACEHOLDER_HINTS):
        return True
    # AWS docs ALWAYS suffix demo keys with EXAMPLE
    if "EXAMPLE" in match:
        return True
    # очень короткое значение — почти наверняка fake (но не для PEM/префиксных)
    structured_prefixes = ("sk-ant-", "sk-proj-", "ghp_", "ghs_", "ghr_", "ghu_", "gho_", "hf_", "AKIA", "AIza")
    if len(match) < 20 and not any(match.startswith(p) for p in structured_prefixes):
        return True
    return False


def line_is_disabled(line: str) -> bool:
    return bool(DISABLE_COMMENT.search(line))


def scan_text(text: str, source: str) -> list[str]:
    findings: list[str] = []
    if any(h in source for h in IGNORE_PATH_HINTS):
        return findings
    if "BEGIN PUBLIC KEY" in text:  # public keys are not secrets
        return findings

    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        if line_is_disabled(line):
            continue
        for label, pat in SECRET_PATTERNS:
            for m in pat.finditer(line):
                if is_placeholder(line, m.group(0)):
                    continue
                preview = m.group(0)[:8] + "…"
                findings.append(f"{source}:{lineno}: {label} ({preview})")
        for label, pat in CONTEXT_PATTERNS:
            # для context-паттернов is_placeholder не применяется — слишком много
            # ложных срабатываний (e.g. example.com в hostname). Только disable-comment.
            if pat.search(line):
                findings.append(f"{source}:{lineno}: {label}")
    return findings


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def is_git_secret_command(cmd: str) -> bool:
    """git commit / git push / git add (но НЕ status/diff/log/show)."""
    if "git " not in cmd:
        return False
    norm = " ".join(cmd.split()).lower()
    triggers = ("git commit", "git push", "git add ", "git add.", "git add -", "&& git add")
    return any(t in norm for t in triggers)


def scan_staged_via_gitleaks(cwd: str | None) -> str | None:
    """Возвращает текст findings или None если ничего не найдено / gitleaks недоступен."""
    if not shutil.which("gitleaks"):
        return None
    try:
        out = subprocess.run(
            ["gitleaks", "detect", "--staged", "--no-banner", "--redact", "--report-format", "csv"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=cwd,
        )
        if out.returncode == 1 and out.stdout.strip():
            lines = out.stdout.strip().splitlines()
            return "\n".join(lines[:10])
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def scan_staged_via_regex(cwd: str | None) -> list[str]:
    """Fallback: git diff --cached → regex."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        if out.returncode != 0:
            return []
        return scan_text(out.stdout, "<staged-diff>")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("hook_event_name") != "PreToolUse":
        sys.exit(0)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {})

    # ─── Bash: git commit/push/add ──────────────────────────────────
    if tool == "Bash":
        cmd = inp.get("command", "")
        if not is_git_secret_command(cmd):
            sys.exit(0)
        # cwd берём из tool_input если есть, иначе из переменной
        cwd = inp.get("cwd")

        gitleaks_out = scan_staged_via_gitleaks(cwd)
        if gitleaks_out:
            block(
                "🚨 SECRET DETECTED in staged files (gitleaks):\n"
                f"{gitleaks_out}\n\n"
                "Не делай commit. Действия:\n"
                "  1. Удали секрет из файла — замени литерал на os.environ['NAME']\n"
                "  2. Положи реальное значение в .env (он в .gitignore) или в shell-переменную\n"
                "  3. Если файл с секретом не должен быть в git: git rm --cached <file>\n"
                "  4. Если ключ уже видел кто-то — отозви его в панели сервиса"
            )

        # fallback если gitleaks нет
        regex_findings = scan_staged_via_regex(cwd)
        if regex_findings:
            joined = "\n  ".join(regex_findings[:10])
            block(
                "🚨 SECRET DETECTED in staged diff (regex fallback):\n"
                f"  {joined}\n\n"
                "Не делай commit. Замени литералы на env vars.\n"
                "Установи gitleaks для более точного скана: pip install gitleaks (или brew install gitleaks)."
            )
        sys.exit(0)

    # ─── Write/Edit: содержимое нового/изменённого файла ────────────
    if tool in ("Write", "Edit"):
        path = inp.get("file_path") or inp.get("path", "")
        content = ""
        if tool == "Write":
            content = inp.get("content", "")
        else:  # Edit
            content = (inp.get("new_string") or "") + "\n" + (inp.get("content") or "")
        if not content.strip():
            sys.exit(0)

        findings = scan_text(content, path or "<edit>")
        if findings:
            joined = "\n  ".join(findings[:10])
            block(
                "🚨 SECRET DETECTED in content you're about to write:\n"
                f"  {joined}\n\n"
                "Не сохраняй ключи в коде. Используй env vars:\n"
                "  Python:  import os; key = os.environ['KEY_NAME']\n"
                "  Shell:   export KEY_NAME=...\n"
                "  .env:    KEY_NAME=...   (и .env должен быть в .gitignore)\n\n"
                "Если это намеренный пример/fixture — добавь '# noqa: secret' в строку."
            )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
