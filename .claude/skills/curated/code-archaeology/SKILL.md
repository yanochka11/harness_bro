---
name: code-archaeology
description: Use when joining an unfamiliar codebase, before refactoring legacy code, or when user asks "разберись в коде", "что тут происходит", "trace where X is used", "explain this module". Maps codebase structure, finds entry points, identifies hot files via git log churn, surfaces architectural patterns. Read-only investigation.
allowed-tools: [Read, Grep, Glob, Bash]
model: sonnet
---

# Code Archaeology

Goal: build a mental model of an unknown codebase in 10-15 minutes before touching anything.

## Phase 1: Topology
- `tree -L 2 -I 'node_modules|__pycache__|.git'` — top-level structure
- Read `README.md`, `pyproject.toml` / `package.json` / `Cargo.toml`
- Identify entry points: main.py, run.py, server.py, index.ts, cmd/

## Phase 2: Hot files (most-changed = most important)
`git log --pretty=format: --name-only --since=3.months | sort | uniq -c | sort -rg | head -20`

## Phase 3: Data flow
For each entry point: trace inputs (CLI args, HTTP routes) to outputs.
- `grep -rn "def main\|if __name__" --include='*.py'`
- For services: request → handler → service → repo → response

## Phase 4: Patterns
- DI/IoC? Look for factory functions, container.py, conftest.py
- Domain model? entities/, models/, domain/
- Test strategy? `find . -name 'test_*' -o -name '*.spec.*' | head`

## Output format
Architecture summary

Stack: <languages, frameworks>
Entry points: <files + purpose>
Hot files (3 mo): <top 10 with #commits>
Key abstractions: <classes/modules and role>
Data flow: <high-level text diagram>
Pain points: <code smells, TODO clusters, deprecation>


## Hard rules
- READ-ONLY — никогда не модифицировать в этом скилле
- Cite file:line for every claim
- Don't trust filenames; verify by reading
