<div align="center">

<br/>

# `harness_bro`

### Конфигурация `.claude/` для Claude Code, заточенная под ML/AI-разработку.

<br/>

[![GitHub](https://img.shields.io/badge/github-yanochka11/harness__bro-1f1f23?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yanochka11/harness_bro)
[![License](https://img.shields.io/badge/license-MIT-eab308?style=for-the-badge)](LICENSE)
[![Install](https://img.shields.io/badge/install-30s-10b981?style=for-the-badge)](#-установка)

[![Сайт проекта](https://img.shields.io/badge/●_сайт_проекта-yanochka11.github.io%2Fharness__bro-10b981?style=flat-square&labelColor=0a0a0a)](https://yanochka11.github.io/harness_bro/)

<sub><code>v1.0</code> · Linux · macOS · WSL2 · `python ≥ 3.10`</sub>

<br/>

[Установка ↓](#-установка) ·
[Что внутри](#-что-внутри) ·
[Триггеры](#-триггеры) ·
[MLSpace / proxy](#-mlspace--proxy)

<br/>

</div>

---

## 🚀 Установка

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

По умолчанию ставится в **текущую директорию**. Если запущено из `$HOME` — в `$HOME/harness_bro`. Можно ввести свой путь в промпте или передать `--target`.

Скрипт проверяет зависимости (`python ≥ 3.10`, `git` — обязательны; `node`+`npm` — нужны только для MCP-серверов через `npx`), клонирует репо во временную директорию, копирует `.claude/`, рендерит `CLAUDE.md` и `.mcp.json` под workspace, делает хуки исполняемыми. По завершении автоматически запускает Claude Code с `CLAUDE_CONFIG_DIR=<target>/.claude-account` — на первом старте инициируется login flow. **Идемпотентный** — существующие файлы бэкапятся в `<имя>.bak`.

<details>
<summary><b>🐍 Под conda</b></summary>

```bash
# (1) активировать env с python ≥ 3.10
conda activate ваше-окружение

# (2) проверить
python --version           # должно быть >=3.10
which python && which git  # доступны в PATH

# (3) (если будут использоваться MCP) поставить node в этот env
conda install -c conda-forge nodejs                 # >=20.x

# (4) поставить Claude Code CLI
npm install -g @anthropic-ai/claude-code
which claude                                         # должен указывать на npm prefix

# (5) запустить установщик
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Если `claude` в shell прокинут на алиас (например `claude-account` для multi-account setup через `CLAUDE_CONFIG_DIR`), используйте свою обёртку. Установщик не зависит от PATH'а `claude` — только проверяет наличие CLI и предупреждает.

</details>

#### После установки

Установщик сам запустит Claude Code в свежепоставленной workspace. Если первый раз — будет login flow (URL в терминале, открыть в браузере). Credentials сохранятся в `<target>/.claude-account/`.

Повторный запуск:

```bash
cd <target>
CLAUDE_CONFIG_DIR=$PWD/.claude-account claude
```

Если в shell стоит alias-заглушка (типа `alias claude="echo 'Use specific commands: claude-username'"`, частый случай в MLSpace/JupyterHub), установщик сам это детектит и в подсказке к повторному запуску подставляет прямой путь к бинарю (`/home/jovyan/.local/bin/claude` или аналог).

Внутри сессии:

```
/env                       снимок окружения (conda, python, HF_HOME, GPU)
/gpu  /procs  /git-status  быстрые состояния
напиши hello.py …          запрос — субагент подбирается по триггерам
Ctrl+D  или  /exit         выход
```

История сессий — в `<target>/.claude-account/sessions/`.

<details>
<summary><b>Флаги установщика</b></summary>

```
--target <путь>          куда поставить (по умолчанию $PWD; если $PWD=$HOME → $HOME/harness_bro)
--tools / --no-tools     ставить ruff + mypy + pytest
--banned-paths a,b,c     запрет записи в эти пути (для hook nfs_guard)
--yes                    использовать дефолты, ничего не спрашивать
```

Передаются через `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh \
  | bash -s -- --target /opt/harness_bro --tools --yes
```

</details>

---

## 📦 Что внутри

```
agents/         5    bug-hunter · code-writer · runner · paper-reader · researcher
hooks/          6    nfs_guard · secret_guard · validate_python · auto_save_skill
                     · auto_fix_suggest · statusline
commands/      18    /lint /format /typecheck /pytest /coverage /tex-build
                     /env /gpu /procs /diskcfs /hf-cache
                     /git-status /find-todo /last-error /deps /wandb-runs
                     /run-dirs /clean-tmp
skills/        82    29 curated + 53 ported в плоской структуре (top-level,
                     видны в /skills). Плюс 17 sub-skills внутри портов
                     skill-factory / super-hermes / evals / gstack —
                     загружаются on-demand самими родительскими скилами.
                     Покрытие: HuggingFace, axolotl, unsloth, TRL, vLLM,
                     llama.cpp, evaluating-llms-harness, code-review,
                     github-pr-workflow, arxiv, latex, data-viz, diagrams,
                     dspy, outlines.
mcp/            7    filesystem · github · tmux · context7
                     memory · sequential-thinking · arxiv
memory/              recipes/ · decisions/ · gotchas/ · style/
```

#### Свойства

🛡 **`secret_guard`** блокирует Write/Edit и `git commit/push/add`, если в содержимом ключи OpenAI, Anthropic, HuggingFace, GitHub, AWS, GCP, Slack, Stripe, W&B, JWT, PEM или пароли в DB-strings.

🧠 **Память между сессиями.** Успешный фикс кладётся в `recipes/<имя>.md` с regex-паттерном. При повторе той же ошибки `auto_fix_suggest` находит запись и подсказывает.

🚫 **Anti-hallucination.** Скиллы `verify-claim` и `web-research` обязывают проверять факты до утверждения (триггеры `latest`, `какая версия`, `best practices`).

🔁 **Самообучение.** `auto_save_skill` фиксирует устойчивые tool-паттерны (≥ 3 повторов, фильтр шума) как черновики скиллов.

⚡ **43 read-only команды** в `permissions.allow` + `defaultMode: auto` — типичные `cat` / `ls` / `git status` / `pytest` выполняются без явного подтверждения.

🌍 **Без жёстких путей.** Всё через env vars и подстановку в шаблонах.

<br/>

<details>
<summary><b>📖 Подробное описание каждого компонента</b></summary>

<br/>

#### Субагенты — `.claude/agents/`

Активируются автоматически по триггерным словам в сообщении. Каждый — отдельный системный промпт с ограниченным набором инструментов и собственным жизненным циклом.

| Агент | Триггеры | Что делает |
|:--|:--|:--|
| **`code-writer`** | напиши, реализуй, добавь, рефактор, переписать, имплементируй, implement, refactor, write | Senior-level Python / JS / Go / Rust. Сначала читает 3–5 соседних файлов через Grep/Glob, чтобы понять конвенции проекта (импорты, docstring-стиль, error handling). Затем правит код через Edit / Write. После — AST-валидация и `pytest -x`. |
| **`bug-hunter`** | падает, ошибка, traceback, не работает, exception, OOM, slow, memory leak | Не лечит вслепую. Читает логи / трейс, минимально воспроизводит баг, формулирует 2–3 гипотезы и ранжирует их. Только потом пишет точечный фикс + регрессионный тест. |
| **`runner`** | запусти, run, train, fine-tune, evaluate, мониторинг, status, stop run | Длинные процессы запускает только в фоне (`nohup`), пишет лог в `runs/<task>/<ts>/run.log`. Никогда не блокирует чат. Умеет мониторить через `pgrep`, `tail -F`, `nvidia-smi` и аккуратно останавливать через `pkill -TERM`. |
| **`paper-reader`** | прочитай статью, summarize paper, arxiv, что в этом пейпере, ключевые идеи статьи | Скачивает arxiv / HF papers / локальный PDF, читает и возвращает структурный конспект: ключевые контрибуции, метод, результаты, ограничения. |
| **`researcher`** | исследуй, найди в интернете, research, что нового в, latest, recent, current best practices, какая версия | Многоисточниковый веб-ресёрч. Декомпозирует вопрос → план поиска → `WebSearch` + `WebFetch` + `context7` → синтез с цитатами и retrieval-датами. Работает в связке с `verify-claim`. |

#### Хуки — `.claude/hooks/`

Срабатывают автоматически на жизненные события Claude Code (`PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit`). Регистрация в `.claude/settings.json`.

| Хук | Когда срабатывает | Что делает |
|:--|:--|:--|
| **`nfs_guard.py`** | `PreToolUse` (Write / Edit / Bash) | Блокирует запись в любые пути, перечисленные в env-var `HARNESS_BANNED_PATHS`. Полезно на NFS-кластерах вроде MLSpace, где `/home/jovyan` read-only. Без env-var — no-op. |
| **`secret_guard.py`** | `PreToolUse` (Write / Edit / Bash) | Сканирует содержимое на API-ключи: OpenAI, Anthropic, HuggingFace, GitHub PAT/OAuth, AWS, GCP, Slack, Stripe, W&B, JWT, PEM, пароли в DB-strings. При обнаружении — `decision: block`, операция отменяется. |
| **`validate_python.py`** | `PostToolUse` (Write / Edit на `.py`) | После каждой записи Python-файла прогоняет AST + `py_compile` + `ruff F-rules` (F821 undefined name, F823 local-before-assignment, F811 redefinition). Сломанный код блокируется до того, как пойдёт дальше. |
| **`auto_save_skill.py`** | `PostToolUse` (любой) и `Stop` | Записывает все tool-вызовы в `.claude/state/`. На `Stop` смотрит, не повторился ли устойчивый паттерн ≥ 3 раз с фильтром шума — если да, кладёт черновик скилла в `.claude/skills/auto/`. |
| **`auto_fix_suggest.py`** | `PostToolUse` (Bash) | После падения `pytest` / `ruff` / `mypy` читает stderr, ищет matching рецепт в `.claude/memory/recipes/` по regex-паттерну и инжектит подсказку Claude. Цикл «тест упал → рецепт найден → фикс применён» работает на втором повторе ошибки за 0 токенов на расследование. |
| **`statusline.sh`** | каждый рендер строки статуса | Показывает в нижней строке Claude Code сводку: модель, текущий каталог, GPU-загрузка, количество фоновых процессов. |

#### Быстрые команды — `.claude/commands/`

Read-only снимки состояния. Вводятся как `/<name>` в Claude Code TUI.

**Код и тесты (6):**

| Команда | Действие |
|:--|:--|
| `/lint` | Запуск всех настроенных линтеров проекта (ruff, mypy, eslint, …) |
| `/format` | Авто-форматирование Python (`ruff format`) |
| `/typecheck` | Проверка типов (`mypy` или `pyright`) |
| `/pytest` | `pytest -x --ff` (last-failed first, fail-fast) |
| `/coverage` | `pytest --cov` с coverage-репортом |
| `/tex-build` | Сборка LaTeX через `latexmk` (с авто-определением bib и пере-прогонами) |

**Окружение (5):**

| Команда | Действие |
|:--|:--|
| `/env` | Conda env, Python, ALPHA_ROOT, HF, W&B, кол-во GPU |
| `/gpu` | Снимок `nvidia-smi` |
| `/procs` | Запущенные python / training / eval процессы (пользовательские + GPU compute apps) |
| `/diskcfs` | Размер HF-кэша (использует `$HF_HOME`) |
| `/hf-cache` | HuggingFace кэш: total + top-10 моделей + top-5 датасетов |

**Состояние (7):**

| Команда | Действие |
|:--|:--|
| `/git-status` | `git status` + diff stats + последние коммиты |
| `/find-todo` | TODO / FIXME / HACK маркеры в коде |
| `/last-error` | Последние 50 строк с error / traceback из `runs/` |
| `/deps` | Установленные Python-пакеты (top-50 по частоте импорта) |
| `/wandb-runs` | Последние 10 W&B runs (локальных + summary) |
| `/run-dirs` | Последние 10 run-директорий в `$ALPHA_ROOT/runs/` (размер + последняя строка лога) |
| `/clean-tmp` | Что лежит в `/tmp/` от текущего пользователя (info-only, не удаляет) |

#### Скиллы — `.claude/skills/`

99 SKILL.md файлов всего: **82 user-invocable** на верхнем уровне (29 curated + 53 ported) + **17 sub-skills** внутри портированных пакетов (skill-factory, super-hermes, evals, gstack), которые подгружаются on-demand их родителями. В `/skills` Claude Code показывает только верхний уровень. Каждый SKILL.md — markdown с YAML-frontmatter (`name`, `description` с триггерными фразами); описание ≤ 1024 символа, иначе Claude его пропускает.

**Curated — собственные / ключевые** (29 top-level + 17 sub-skills во вложенных пакетах):

- *Workflow:* `verify-claim`, `web-research`, `record-recipe`, `self-improve`, `brainstorming`, `writing-plans`, `systematic-debugging`, `test-driven-development`
- *Безопасность:* `secret-guard`, `pre-commit-guard`
- *Документы:* `docx`, `pdf`, `pptx`, `xlsx`, `latex-writing`
- *Визуализация:* `data-viz` (matplotlib / seaborn / plotly), `diagrams` (mermaid / d2 / plantuml)
- *Поиск и работа с кодом:* `smart-grep`, `code-archaeology`, `dependency-audit`, `perf-profiler`
- *Эвалуация:* `evals/` (eval-audit, write-judge-prompt, error-analysis, …)
- *Скилл-инфраструктура:* `skill-creator`, `mcp-builder`, `meta/` (skill-factory, skill-optimizer, super-hermes)
- *Прочее:* `using-git-worktrees`, `verification-before-completion`, `requesting-code-review`, `finishing-a-development-branch`, `webapp-testing`, `async-task-runner`, `gstack/` (investigate, plan-eng-review, review)

**Ported (53) — импортированы из проверенных источников:**

- *HuggingFace стек:* `huggingface-hub`, `huggingface-datasets`, `huggingface-llm-trainer`, `huggingface-best`, `huggingface-local-models`, `huggingface-gradio`, `huggingface-papers`, `huggingface-trackio`, `hf-cli`, `hf-mcp`
- *Тренировка LLM:* `axolotl`, `unsloth`, `fine-tuning-with-trl`, `serving-llms-vllm`, `llama-cpp`
- *Эвалуация:* `evaluating-llms-harness`, `huggingface-community-evals`
- *Code-review / git:* `code-review`, `code-simplifier`, `iterate-pr`, `pr-writer`, `github-pr-workflow`, `gh-review-requests`, `github-code-review`, `github-issues`, `github-repo-management`, `github-auth`, `gha-security-review`, `commit`, `create-branch`, `find-bugs`, `security-review`
- *Research / writing:* `arxiv`, `research-paper-writing`, `huggingface-paper-publisher`, `doc-coauthoring`
- *Tooling / dev:* `weights-and-biases`, `python-debugpy`, `jupyter-live-kernel`, `prompt-optimizer`, `claude-code`, `claude-settings-audit`
- *LLM-фреймворки:* `dspy`, `outlines`, `huggingface-tool-builder`
- *Скилл-фабрика:* `skill-authoring`, `skill-writer`, `skill-scanner`, `subagent-driven-development`, `native-mcp`
- *Workflow:* `plan`, `spike`, `codebase-inspection`

Источники: [obra/superpowers](https://github.com/obra/superpowers), [anthropics/skills](https://github.com/anthropics/skills), [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), [getsentry](https://github.com/getsentry), [garrytan/gstack](https://github.com/garrytan/gstack).

#### MCP-серверы — `.mcp.json`

[Model Context Protocol](https://modelcontextprotocol.io/) — стандартизированные внешние инструменты, доступные Claude. Все запускаются через `npx`, лениво — на первый вызов.

| Сервер | Что даёт |
|:--|:--|
| **`filesystem`** | Низкоуровневые fs-операции, scoped к workspace (`@modelcontextprotocol/server-filesystem`). |
| **`github`** | Issues / PR / repo операции. Требует `GITHUB_TOKEN` в env. |
| **`tmux`** | Управление tmux-сессиями (создать / отправить команду / прочитать буфер). |
| **`context7`** | Свежая документация библиотек, актуальнее обучающих данных Claude. |
| **`memory`** | Knowledge graph между сессиями (`@modelcontextprotocol/server-memory`). Граф сущностей и связей, persists в `.claude/memory/mcp-graph.json`. |
| **`sequential-thinking`** | Структурированные цепочки рассуждений (`@modelcontextprotocol/server-sequential-thinking`). Полезно при дебаге сложных гипотез. |
| **`arxiv`** | Поиск и скачивание arxiv-статей (`arxiv-mcp-server`). Дополняет субагент `paper-reader`. |

При первом старте Claude Code попросит подтвердить trust для каждого `.mcp.json`-сервера — это защита от автоматического запуска кода. Подтверждайте только знакомые.

#### Рекомендуемые плагины — `/plugin`

Установить через интерактивный `/plugin` в Claude Code TUI. Хорошо ложатся поверх harness_bro:

| Плагин | Что даёт |
|:--|:--|
| **`superpowers`** | Набор обязательных рабочих скиллов (brainstorming, writing-plans, TDD, systematic-debugging, verification-before-completion) с триггерами и проверкой использования. |
| **`pr-review-toolkit`** | `/review-pr` — мульти-агентный обзор pull-request'а. |
| **`feature-dev`** | Управляемая разработка фичи с архитектурным фокусом и пониманием кодовой базы. |
| **`skill-creator`** | Создание / редактирование / измерение performance скиллов. Дополняет родной `record-recipe`. |
| **`frontend-design`** | Production-grade frontend (если фронт нужен). Уходит от generic AI-эстетики. |
| **`ralph-loop`** | Loop-агент для повторяющихся проверок (status, sweep). |
| **`serena`** | Code intelligence через LSP-подобный backend, ускоряет навигацию. |
| **`github`** | Расширенные операции с GitHub (issues, PRs, releases), дополняет MCP `github`. |

Плагины и skills coexist: плагин-скиллы регистрируются с namespace (`superpowers:brainstorming`), filesystem-скиллы из `.claude/skills/curated/` подгружаются по своим именам.

#### Память — `.claude/memory/`

Постоянная между сессиями. Состояние, которое Claude Code записывает и читает.

| Директория | Назначение |
|:--|:--|
| **`recipes/`** | Решённые проблемы с regex-паттерном для матчинга. Hook `auto_fix_suggest` читает их при падении тестов и подсказывает фикс. Записываются скиллом `record-recipe` после фразы «запомни». |
| **`decisions/`** | Архитектурные решения проекта (что выбрали, почему, что отклонили). Помогает при ревью PR и онбординге. |
| **`gotchas/`** | Подводные камни — нюансы которые легко не заметить (race conditions, edge cases, неочевидные зависимости). |
| **`style/`** | Кодовый стиль проекта в формате памятки (отступы, naming, error handling). Подгружается в контекст code-writer субагента. |

</details>

---

## 🎯 Триггеры

Каждый субагент и скилл объявляет триггерные фразы в YAML-frontmatter. Claude матчит сообщение пользователя с описаниями и активирует подходящий компонент.

| Сообщение | Активирует |
|:--|:--|
| напиши · реализуй · рефактор | `code-writer` |
| падает · traceback · OOM | `bug-hunter` |
| запусти · обучи · evaluate | `runner`  &nbsp;<sub>фон через nohup</sub> |
| прочитай статью · arxiv | `paper-reader` |
| исследуй · latest · какая версия | `researcher` + `verify-claim` |
| коммит · push | `secret-guard` + хук |
| запомни этот рецепт | `record-recipe` |
| оптимизируй setup | `self-improve` |
| нарисуй график · matplotlib | `data-viz` |
| нарисуй схему · mermaid | `diagrams` |
| статья в латех · overleaf | `latex-writing` |
| найди где X · callers Y | `smart-grep` |

#### Цикл авто-фикса

```
тест/линтер падает      →  auto_fix_suggest читает stderr
                        →  grep recipes/ по regex
                        →  matching рецепт инжектится Claude
                        →  фикс применяется
«запомни»               →  record-recipe пишет файл
                        →  следующий раз: 0 токенов на расследование
```

---

## 🌐 MLSpace / proxy

```bash
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1,.cluster.local"

curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик находит `HTTPS_PROXY`, маскирует пароль в логах, прокидывает в `npm config`, проверяет доступность `github.com`. При недоступности — печатает подсказку.

> ⚠ **Не публикуйте proxy URL с паролем в чате, документации, коммитах, скриншотах.** Храните в `~/.bashrc` / `~/.zshrc` / `~/.netrc` (chmod 600) или secrets-менеджере. Если случайно засветили — смените пароль на проксе сразу.

---

<details>
<summary><b>⚙️ Опциональные env vars</b></summary>

```bash
export HF_HOME=$PWD/.cache/huggingface          # кэш HuggingFace
export HARNESS_BANNED_PATHS=/home/readonly,...  # для nfs_guard hook
export GITHUB_TOKEN=ghp_…                       # для github MCP-сервера
export WANDB_DIR=$PWD/wandb                     # локальные W&B runs
```

Все необязательные. Без них всё работает.

</details>

<details>
<summary><b>🔧 Кастомизация</b></summary>

**Свой скилл:**

```bash
mkdir -p .claude/skills/curated/мой-скилл
cat > .claude/skills/curated/мой-скилл/SKILL.md <<'EOF'
---
name: мой-скилл
description: Use when [триггерные фразы]. Помогает с [...]
---
EOF
```

**Своя slash-команда:**

```bash
echo 'Что показывает: !`echo привет`' > .claude/commands/foo.md
# /foo доступна сразу
```

**Свой хук:** `.py` читает JSON со stdin, при блокировке печатает `{"decision":"block","reason":"…"}`. Регистрируется в `.claude/settings.json`.

**Отключить хук:** удалите его блок из `settings.json`. Файл `.py` можно оставить.

</details>

<details>
<summary><b>🩺 Troubleshooting</b></summary>

| Проблема | Решение |
|:--|:--|
| `claude: command not found` | `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет / `< 3.10` | `apt install python3` или `brew install python` |
| `curl: (6) Could not resolve host` | DNS / прокси, см. [MLSpace](#-mlspace--proxy) |
| Хук блокирует команду | `cat .claude/hooks/имя.py` чтобы понять. Чтобы отключить — переименуйте `.py` |
| `secret_guard` ложно срабатывает | `# noqa: secret` в строке |
| Обновление | Перезапустить `curl … | bash` из той же директории — существующие файлы бэкапятся в `*.bak` |

</details>

<details>
<summary><b>❓ FAQ</b></summary>

- **Без GPU работает?** Да. `/gpu` молчит, если `nvidia-smi` нет. ML-скиллы не активируются, если их не вызывать.
- **Windows?** WSL2 — да. Нативный — не тестировался.
- **Чем отличается от Anthropic plugin marketplace?** Маркетплейс — каталог плагинов. `harness_bro` — готовая `.claude/` с дефолтами и установщиком в одну команду.
- **Перезапишет правки при обновлении?** Существующие файлы автобэкапятся в `<имя>.bak`. Свои файлы (новые скиллы / хуки) не конфликтуют со штатными именами.

</details>

---

<div align="center">

<sub>Built on top of <a href="https://claude.ai/code">Claude Code</a> · Skills imported from <a href="https://github.com/obra/superpowers">superpowers</a>, <a href="https://github.com/anthropics/skills">anthropic-skills</a>, <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a>, <a href="https://github.com/getsentry">sentry</a>, <a href="https://github.com/garrytan/gstack">gstack</a></sub>

<sub><a href="https://github.com/yanochka11/harness_bro">github.com/yanochka11/harness_bro</a> · <a href="LICENSE">MIT</a></sub>

</div>
