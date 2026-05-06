# harness_bro — Claude Code project context

## Working directory
`/mnt/virtual_ai0001071-04017_SR004-nfs1/NFS1-SR008/users/iana_kulichenko/alpha`

## Filesystem rules
- Writeable: `/mnt/virtual_ai0001071-04017_SR004-nfs1/NFS1-SR008/users/iana_kulichenko/alpha/**`
- No banned write-paths (set HARNESS_BANNED_PATHS env var to enable nfs_guard)
- HF cache: `${HF_HOME:-~/.cache/huggingface}` (configurable via `$HF_HOME`)

## Style
- Прямо, плотно, технически. Без хедж-фраз.
- Read before write. Перед правкой — `Read`/`Grep`/`Glob` понять структуру.
- Match existing style — импорты, docstring, type hints, error handling.
- При неуверенности — запустить проверку (`cat` / `grep` / `pytest`), не угадывать.
- Tradeoffs называть явно. Допущения проговаривать.

## Code quality
- Python: type hints, docstrings для public API, без bare `except`.
- Хук `validate_python.py` после Write/Edit `.py`: AST + `py_compile` + `ruff F-rules` (F821/F823/F811).
- Тесты: `/pytest` (= `pytest -x --ff --tb=short`).
- Лайнт: `/lint` (ruff + mypy).
- Коммиты: small, present tense ("add X", не "added X").

## Long-running команды
- `nohup … &` с логом в `/mnt/virtual_ai0001071-04017_SR004-nfs1/NFS1-SR008/users/iana_kulichenko/alpha/runs/<task>/<ts>/`.
- Не блокировать чат foreground'ом training/eval — делегировать subagent `runner`.
- `pkill -TERM` (graceful), `-KILL` только если первое не сработало.

## Subagents (5) — `.claude/agents/`, через Task tool
- **code-writer** — implement / refactor / write tests. Триггеры: напиши, реализуй, рефактор, implement.
- **bug-hunter** — диагноз failures / OOM / regressions. Триггеры: падает, traceback, OOM.
- **runner** — старт/мониторинг/стоп долгих процессов. Триггеры: запусти, train, fine-tune, evaluate.
- **paper-reader** — конспект arxiv/HF/PDF статей. Триггеры: прочитай статью, summarize paper.
- **researcher** — multi-source веб-ресёрч. Триггеры: исследуй, latest, recent, какая версия.

## Slash commands (18) — `.claude/commands/`
- **Code (6):** `/lint`, `/format`, `/typecheck`, `/pytest`, `/coverage`, `/tex-build`
- **Окружение (5):** `/env`, `/gpu`, `/procs`, `/diskcfs`, `/hf-cache`
- **Состояние (7):** `/git-status`, `/find-todo`, `/last-error`, `/deps`, `/wandb-runs`, `/run-dirs`, `/clean-tmp`

## MCP servers (7) — `.mcp.json`
- **filesystem** — fs-операции, scoped к workspace.
- **github** — issues / PR / repo (нужен `GITHUB_TOKEN`).
- **tmux** — управление сессиями.
- **context7** — свежая документация библиотек.
- **memory** — knowledge graph между сессиями (`mcp-graph.json`).
- **sequential-thinking** — структурированные цепочки рассуждений.
- **arxiv** — поиск/скачивание arxiv-статей.

## Hooks (6) — `.claude/hooks/`, регистрация в `settings.json`
1. **nfs_guard.py** — PreToolUse: блокирует Write/Edit в путях из `$HARNESS_BANNED_PATHS`. Без env — no-op.
2. **secret_guard.py** — PreToolUse: сканит содержимое на API-ключи (OpenAI/Anthropic/HF/GitHub/AWS/GCP/Slack/Stripe/W&B/JWT/PEM) и блокирует commit со staged-секретами.
3. **validate_python.py** — PostToolUse: AST + `py_compile` + ruff F-rules для `.py`.
4. **auto_save_skill.py** — PostToolUse + Stop: записывает tool-вызовы; устойчивые паттерны (≥3 повтора) кладёт черновиком в `.claude/skills/auto/`.
5. **auto_fix_suggest.py** — PostToolUse Bash: после fail `pytest`/`ruff`/`mypy` ищет рецепт в `memory/recipes/` по regex и инжектит подсказку.
6. **statusline.sh** — каждый рендер строки: модель, cwd, GPU%, py-procs.

## Skills — `.claude/skills/`
- 99 SKILL.md всего: **82 top-level** (29 curated + 53 ported, видны в `/skills`) + **17 sub-skills** во вложенных портах (skill-factory, super-hermes, evals, gstack — подгружаются on-demand родителями).
- Frontmatter: `name`, `description` ≤1024 символа (Claude обрезает длиннее).

## Memory — `.claude/memory/`
- `MEMORY.md` — индекс, одна строка на запись.
- `recipes/<slug>.md` — фикс-паттерны c regex `pattern:` для `auto_fix_suggest`.
- `decisions/<slug>.md` — архитектурные решения.
- `gotchas/<slug>.md` — что не работало.
- `style/<slug>.md` — пользовательские предпочтения.

При ошибке — сначала `grep` по `.claude/memory/`. После успешного фикса предложить запись через skill `record-recipe`.

## Permissions — `.claude/settings.json`
- 43 allow-правил (read-only `cat`/`ls`/`grep`/`pytest`/`git status` без prompt).
- 4 deny-правила.
- `defaultMode: auto` + `skipAutoPermissionPrompt: true` — автономная работа.
