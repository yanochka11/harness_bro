---
name: smart-grep
description: Use when user asks find где используется X, all callers, find definition, rename across codebase, find all imports, trace usage. Picks right tool (rg, ast-grep, semgrep) for language and intent.
allowed-tools: [Bash, Read, Grep, Glob]
model: sonnet
---

# Smart Grep

## Tool choice
- Plain text → `rg` (already wrapped by Grep tool)
- Syntactic Python search → `ast-grep` (если установлен)
- Cross-language semantic → `semgrep --pattern` (медленно, точно)
- Quick symbol jump → ctags / pygrep

## Common patterns

### Callers of `foo()` in Python
```bash
rg --type py -n '\bfoo\(' --glob '!**/test_*'
```
```bash
ast-grep --pattern 'foo($$$)' --lang python
```

### Imports of module X
```bash
rg --type py -n '^(from\s+pkg\.X\s+import|import\s+pkg\.X)' .
```

### Subclasses of BaseFoo
```bash
ast-grep --pattern 'class $A(BaseFoo): $$$' --lang python
```

### Definitions only (skip references)
```bash
rg --type py -n '^(def|class)\s+TARGET\b'
```

### TODO/FIXME with location
```bash
rg -n 'TODO|FIXME|HACK|XXX' --no-heading | sort -u
```

### Rename preview (don't apply)
```bash
rg -l 'old_name' | head
```

## Hard rules
- For code: prefer ast-grep over rg (avoids false positives in strings/comments)
- For renames: ALWAYS show preview before applying
- Default exclude: node_modules, __pycache__, .git, venv, build
