---
name: dependency-audit
description: Use to audit project dependencies for outdated packages, security vulnerabilities, version conflicts, unused imports, lockfile drift. Triggers проверь зависимости, outdated, vulnerabilities, security, что-то сломалось после установки.
allowed-tools: [Bash, Read]
model: sonnet
---

# Dependency Audit

## Python
- `pip list --outdated` — что устарело
- `pip check` — version conflicts
- `pip-audit` — CVE scan (если установлен)
- `pipdeptree --warn fail` — dep graph + конфликты
- `vulture .` — unused code/imports

## Node
- `npm outdated`
- `npm audit --production`
- `npx depcheck` — unused deps
- `npm ls` — dep tree

## Rust / Go
- `cargo outdated && cargo audit`
- `go list -u -m all && govulncheck ./...`

## Output format
Dependency audit
Outdated (significant)

pkg: current → latest (release date)

Vulnerabilities

pkg@ver: CVE-ID severity=H/M/L: one-line desc

Conflicts

pkg: required by A (>=X) and B (<Y)

Unused

pkg: imported nowhere

Recommendations

action — reason


## Hard rules
- NEVER auto-update without explicit user OK
- For CVEs: surface severity + exploit availability
- Distinguish dev vs prod dependencies
