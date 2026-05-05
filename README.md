<div align="center">

# `harness_bro`

**Конфигурация `.claude/` для Claude Code, заточенная под ML/AI-разработку.**

[![License](https://img.shields.io/badge/license-MIT-1f6feb?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%C2%B7%20macos%20%C2%B7%20wsl-1f6feb?style=flat-square)](#)
[![Install](https://img.shields.io/badge/install-30s-1f6feb?style=flat-square)](#установка)

[Установка](#установка) · [Что внутри](#что-внутри) · [Триггеры](#триггеры) · [MLSpace / proxy](#mlspace--proxy) · [Подробнее ↓](#)

</div>

<br/>

## Установка

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик проверяет зависимости (`python ≥ 3.10`, `node`, `npm`, `git`), клонирует репозиторий во временную директорию, разворачивает `.claude/` в `~/harness`, рендерит `CLAUDE.md` и `.mcp.json` из шаблонов с подстановкой пути. Идемпотентный — можно перезапускать.

```bash
cd ~/harness && claude
```

<details>
<summary><b>Флаги установщика</b></summary>

```
--target <путь>          куда поставить (по умолчанию ~/harness)
--tools / --no-tools     ставить ruff + mypy + pytest
--banned-paths a,b,c     запрет записи в эти пути (для hook nfs_guard)
--yes                    ничего не спрашивать (использовать дефолты)
```

Передаются через `bash -s --`:

```bash
curl -fsSL https://.../install.sh | bash -s -- --target /opt/harness --tools --yes
```

</details>

<br/>

## Что внутри

| Слой | Состав |
|:--|:--|
| **5 субагентов** | `code-writer` `bug-hunter` `runner` `paper-reader` `researcher` |
| **6 хуков** | `nfs_guard` `secret_guard` `validate_python` `auto_save_skill` `auto_fix_suggest` `statusline` |
| **18 быстрых команд** | `/lint` `/format` `/typecheck` `/pytest` `/coverage` `/tex-build` · `/env` `/gpu` `/procs` `/diskcfs` `/hf-cache` · `/git-status` `/find-todo` `/last-error` `/deps` `/wandb-runs` `/run-dirs` `/clean-tmp` |
| **99 скиллов** | 46 curated + 53 ported (HuggingFace, axolotl/unsloth/TRL, vLLM, llama.cpp, lm-eval-harness, code-review, github-flow, arxiv, latex, data-viz, diagrams, dspy, outlines) |
| **4 MCP-сервера** | `filesystem` `github` `tmux` `context7` |
| **Память** | `recipes/` (regex pattern для авто-фикса) · `decisions/` · `gotchas/` · `style/` |

**Ключевые свойства**

- Хук `secret_guard` блокирует Write/Edit и `git commit/push/add` с ключами OpenAI, Anthropic, HuggingFace, GitHub, AWS, GCP, Slack, Stripe, W&B, JWT, PEM, DB-strings.
- Успешный фикс с regex-паттерном кладётся в `.claude/memory/recipes/`. При повторе той же ошибки `auto_fix_suggest` находит запись и подсказывает решение.
- Скиллы `verify-claim` и `web-research` обязывают проверять факты перед утверждением (триггеры: `latest`, `какая версия`, `best practices`).
- Хук `auto_save_skill` фиксирует устойчивые tool-паттерны (≥ 3 повторов, фильтр шума) как черновики скиллов.
- 43 read-only команды в `permissions.allow` + `defaultMode: auto` — типичные `cat`/`ls`/`git status`/`pytest` выполняются без явного подтверждения.
- Никаких жёстко прописанных путей: всё через env vars и подстановку в шаблонах.

<br/>

## Триггеры

Каждый субагент и скилл объявляет триггерные фразы в YAML-frontmatter. Claude матчит сообщение пользователя с описаниями и активирует подходящий компонент.

| Сообщение | Активирует |
|:--|:--|
| напиши / реализуй / рефактор | `code-writer` |
| падает / traceback / OOM | `bug-hunter` |
| запусти / обучи / evaluate | `runner` (фон через nohup) |
| прочитай статью / arxiv | `paper-reader` |
| исследуй / latest / какая версия | `researcher` + `verify-claim` |
| коммит / push | `secret-guard` + хук |
| запомни этот рецепт | `record-recipe` |
| оптимизируй setup | `self-improve` |
| нарисуй график / matplotlib | `data-viz` |
| нарисуй схему / mermaid | `diagrams` |
| статья в латех / overleaf | `latex-writing` |
| найди где X / callers Y | `smart-grep` |

**Цикл авто-фикса**

```
тест/линтер падает  →  auto_fix_suggest читает stderr  →  grep recipes/ по regex
                  →  matching рецепт инжектится Claude  →  фикс применяется
                  →  «запомни» → record-recipe пишет файл  →  следующий раз = 0 токенов
```

<br/>

## MLSpace / proxy

```bash
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"

curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик находит `HTTPS_PROXY`, маскирует пароль в логах, прокидывает в `npm config`, проверяет доступность `github.com`. При недоступности — печатает подсказку.

> Не вставляйте credentials в код или git. Только env vars или `~/.netrc`.

<br/>

<details>
<summary><b>Опциональные env vars</b></summary>

```bash
export HF_HOME=$PWD/.cache/huggingface          # кэш HuggingFace
export HARNESS_BANNED_PATHS=/home/readonly,...  # для nfs_guard hook
export GITHUB_TOKEN=ghp_...                     # для github MCP-сервера
export WANDB_DIR=$PWD/wandb                     # локальные W&B runs
```

Все необязательные. Без них всё работает.

</details>

<details>
<summary><b>Кастомизация</b></summary>

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
# доступна сразу как /foo
```

**Свой хук:** `.py` читает JSON со stdin, при блокировке печатает `{"decision":"block","reason":"..."}`. Регистрируется в `.claude/settings.json`.

**Отключить хук:** удалите его блок из `settings.json` (файл `.py` можно оставить).

</details>

<details>
<summary><b>Troubleshooting</b></summary>

| Проблема | Решение |
|:--|:--|
| `claude: command not found` | `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет / < 3.10 | `apt install python3` или `brew install python` |
| `curl: (6) Could not resolve host` | DNS / прокси, см. [MLSpace](#mlspace--proxy) |
| Хук блокирует команду | `cat .claude/hooks/имя.py` чтобы понять. Чтобы отключить временно — переименуйте `.py` |
| `secret_guard` ложно срабатывает | Добавьте в строку `# noqa: secret` |
| Обновление | `git pull && ./install.sh --target ~/harness --yes` (с авто-бэкапом в `.bak`) |

</details>

<details>
<summary><b>FAQ</b></summary>

- **Без GPU работает?** Да. `/gpu` молчит если нет `nvidia-smi`. ML-скиллы не активируются если их не вызывать.
- **Windows?** WSL2 — да, нативный — не тестировался.
- **Чем отличается от Anthropic plugin marketplace?** Маркетплейс — каталог плагинов. `harness_bro` — готовая `.claude/` с дефолтами и установщиком в одну команду.
- **Перезапишет правки при обновлении?** Существующие файлы автобэкапятся в `<имя>.bak`. Свои новые файлы (скиллы/хуки) не конфликтуют со штатными именами.

</details>

<br/>

---

<div align="center">

[**GitHub**](https://github.com/yanochka11/harness_bro) · [MIT](LICENSE)

<sub>Built on top of <a href="https://claude.ai/code">Claude Code</a>. Skills imported from <a href="https://github.com/obra/superpowers">superpowers</a> · <a href="https://github.com/anthropics/skills">anthropic-skills</a> · <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a> · <a href="https://github.com/getsentry">sentry</a> · <a href="https://github.com/getstack">gstack</a></sub>

</div>
