<div align="center">

<br/>

# harness_bro

Конфигурация `.claude/` для Claude Code, заточенная под ML/AI-разработку.

<sub><code>v1.0</code> · MIT · Linux · macOS · WSL2</sub>

<br/>

[Установка](#установка) ·
[Что внутри](#что-внутри) ·
[Триггеры](#триггеры) ·
[MLSpace / proxy](#mlspace--proxy) ·
[GitHub](https://github.com/yanochka11/harness_bro)

<br/>

</div>

---

## Установка

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик проверит зависимости (`python ≥ 3.10`, `node`, `npm`, `git`), склонирует репозиторий во временную директорию и развернёт `.claude/` в `~/harness`. Идемпотентный — можно перезапускать.

#### После установки

```bash
cd ~/harness         # workspace, где лежит .claude/
claude               # интерактивная TUI-сессия Claude Code
```

Внутри сессии:

```
/env                       снимок окружения (conda, python, HF_HOME, GPU)
/gpu  /procs  /git-status  быстрые состояния
напиши hello.py …          обычный запрос — субагент подбирается по триггерам
Ctrl+D  или  /exit         выход
```

История пишется в `~/harness/.claude/sessions/`.

<details>
<summary>Флаги установщика</summary>

```
--target <путь>          куда поставить (по умолчанию ~/harness)
--tools / --no-tools     ставить ruff + mypy + pytest
--banned-paths a,b,c     запрет записи в эти пути (для hook nfs_guard)
--yes                    использовать дефолты, ничего не спрашивать
```

Передаются через `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh \
  | bash -s -- --target /opt/harness --tools --yes
```

</details>

---

## Что внутри

```
agents/         5    bug-hunter · code-writer · runner · paper-reader · researcher
hooks/          6    nfs_guard · secret_guard · validate_python · auto_save_skill
                     · auto_fix_suggest · statusline
commands/      18    /lint /format /typecheck /pytest /coverage /tex-build
                     /env /gpu /procs /diskcfs /hf-cache
                     /git-status /find-todo /last-error /deps /wandb-runs
                     /run-dirs /clean-tmp
skills/        99    46 curated + 53 ported (HuggingFace, axolotl, unsloth, TRL,
                     vLLM, llama.cpp, lm-eval-harness, code-review, github-flow,
                     arxiv, latex, data-viz, diagrams, dspy, outlines)
mcp/            4    filesystem · github · tmux · context7
memory/              recipes/ · decisions/ · gotchas/ · style/
```

#### Свойства

— **`secret_guard`** блокирует Write/Edit и `git commit/push/add`, если в содержимом ключи OpenAI, Anthropic, HuggingFace, GitHub, AWS, GCP, Slack, Stripe, W&B, JWT, PEM или пароли в DB-strings.

— **Память между сессиями.** Успешный фикс кладётся в `recipes/<имя>.md` с regex-паттерном. При повторе той же ошибки `auto_fix_suggest` находит запись и подсказывает.

— **Anti-hallucination.** Скиллы `verify-claim` и `web-research` обязывают проверять факты до утверждения (триггеры `latest`, `какая версия`, `best practices`).

— **Самообучение.** `auto_save_skill` фиксирует устойчивые tool-паттерны (≥ 3 повторов, фильтр шума) как черновики скиллов.

— **43 read-only команды** в `permissions.allow` + `defaultMode: auto` — типичные `cat` / `ls` / `git status` / `pytest` выполняются без явного подтверждения.

— **Без жёстких путей.** Всё через env vars и подстановку в шаблонах.

---

## Триггеры

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

## MLSpace / proxy

```bash
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"

curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик находит `HTTPS_PROXY`, маскирует пароль в логах, прокидывает в `npm config`, проверяет доступность `github.com`. При недоступности — печатает подсказку.

> Не вставляйте credentials в код или git. Только env vars или `~/.netrc`.

---

<details>
<summary>Опциональные env vars</summary>

```bash
export HF_HOME=$PWD/.cache/huggingface          # кэш HuggingFace
export HARNESS_BANNED_PATHS=/home/readonly,...  # для nfs_guard hook
export GITHUB_TOKEN=ghp_…                       # для github MCP-сервера
export WANDB_DIR=$PWD/wandb                     # локальные W&B runs
```

Все необязательные. Без них всё работает.

</details>

<details>
<summary>Кастомизация</summary>

**Свой скилл**

```bash
mkdir -p .claude/skills/curated/мой-скилл
cat > .claude/skills/curated/мой-скилл/SKILL.md <<'EOF'
---
name: мой-скилл
description: Use when [триггерные фразы]. Помогает с [...]
---
EOF
```

**Своя slash-команда**

```bash
echo 'Что показывает: !`echo привет`' > .claude/commands/foo.md
# /foo доступна сразу
```

**Свой хук** — `.py` читает JSON со stdin, при блокировке печатает `{"decision":"block","reason":"…"}`. Регистрируется в `.claude/settings.json`.

**Отключить хук** — удалите его блок из `settings.json`. Файл `.py` можно оставить.

</details>

<details>
<summary>Troubleshooting</summary>

| Проблема | Решение |
|:--|:--|
| `claude: command not found` | `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет / `< 3.10` | `apt install python3` или `brew install python` |
| `curl: (6) Could not resolve host` | DNS / прокси, см. [MLSpace](#mlspace--proxy) |
| Хук блокирует команду | `cat .claude/hooks/имя.py` чтобы понять. Чтобы отключить — переименуйте `.py` |
| `secret_guard` ложно срабатывает | `# noqa: secret` в строке |
| Обновление | `git pull && ./install.sh --target ~/harness --yes` &nbsp;<sub>авто-бэкап в `.bak`</sub> |

</details>

<details>
<summary>FAQ</summary>

- **Без GPU работает?** Да. `/gpu` молчит, если `nvidia-smi` нет. ML-скиллы не активируются, если их не вызывать.
- **Windows?** WSL2 — да. Нативный — не тестировался.
- **Чем отличается от Anthropic plugin marketplace?** Маркетплейс — каталог плагинов. `harness_bro` — готовая `.claude/` с дефолтами и установщиком в одну команду.
- **Перезапишет правки при обновлении?** Существующие файлы автобэкапятся в `<имя>.bak`. Свои файлы (новые скиллы / хуки) не конфликтуют со штатными именами.

</details>

---

<div align="center">

<sub>Built on top of <a href="https://claude.ai/code">Claude Code</a>. Skills imported from <a href="https://github.com/obra/superpowers">superpowers</a>, <a href="https://github.com/anthropics/skills">anthropic-skills</a>, <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a>, <a href="https://github.com/getsentry">sentry</a>, <a href="https://github.com/getstack">gstack</a>.</sub>

<sub><a href="https://github.com/yanochka11/harness_bro">github.com/yanochka11/harness_bro</a> · <a href="LICENSE">MIT</a></sub>

</div>
