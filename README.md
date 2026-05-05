<div align="center">

# harness_bro

**Готовая среда Claude Code для ML/AI-инженеров.**

Защита от утечки ключей · постоянная память · авто-фикс ошибок · 99 скиллов · 5 субагентов · 18 быстрых команд · 4 MCP-сервера

[![Site](https://img.shields.io/badge/site-yanochka11.github.io-1f6feb?style=for-the-badge)](https://yanochka11.github.io/harness_bro/)
[![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)](LICENSE)
[![Install](https://img.shields.io/badge/install-30s-brightgreen?style=for-the-badge)](#-установка)

[**Сайт**](https://yanochka11.github.io/harness_bro/) · [Установка](#-установка) · [Что внутри](#-что-внутри) · [Триггеры](#-триггеры) · [MLSpace](#mlspace--прокси)

</div>

---

## 🚀 Установка

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Скрипт сам проверит зависимости (`python ≥3.10`, `node`, `npm`, `git`), склонирует репо во временную папку, развернёт конфиг в `~/harness`. Идемпотентно — можно перезапускать.

```bash
cd ~/harness && claude
```

Готово.

<details>
<summary><b>Флаги установщика</b></summary>

```
--target <путь>          куда поставить (по умолчанию ~/harness)
--tools / --no-tools     ставить ruff + mypy + pytest
--banned-paths a,b,c     запрет записи в эти пути (для hook nfs_guard)
--yes                    ничего не спрашивать
```

Пример: `bash -s -- --target /opt/harness --tools --yes`

</details>

---

## 📦 Что внутри

| Слой | Чем рулит |
|---|---|
| 🤖 **5 субагентов** | `code-writer` · `bug-hunter` · `runner` · `paper-reader` · `researcher` |
| 🪝 **6 хуков** | `nfs_guard` · `secret_guard` · `validate_python` · `auto_save_skill` · `auto_fix_suggest` · `statusline` |
| ⚡ **18 быстрых команд** | `/lint` `/format` `/typecheck` `/pytest` `/coverage` `/tex-build` · `/env` `/gpu` `/procs` `/diskcfs` `/hf-cache` · `/git-status` `/find-todo` `/last-error` `/deps` `/wandb-runs` `/run-dirs` `/clean-tmp` |
| 📚 **99 скиллов** | 46 curated + 53 ported (HuggingFace, axolotl/unsloth/TRL, vLLM, llama.cpp, lm-eval-harness, code-review, github-flow, arxiv, latex, data-viz, diagrams, dspy, outlines) |
| 🔌 **4 MCP-сервера** | `filesystem` · `github` · `tmux` · `context7` (свежая документация библиотек) |
| 🧠 **Память** | `recipes/` (с regex для авто-фикса) · `decisions/` · `gotchas/` · `style/` |

### Главное

- 🛡 **Секреты не утекут в git** — хук блокирует Write/Edit и `git commit/push/add` с ключами OpenAI, Anthropic, HF, GitHub, AWS, GCP, Slack, Stripe, W&B, JWT, PEM, DB-strings.
- 🧠 **Память между сессиями** — успешный фикс с regex-паттерном кладётся в `recipes/`. В следующий раз эта же ошибка решается через `auto_fix_suggest` за 0 токенов.
- 🚫 **Без галлюцинаций** — скиллы `verify-claim` и `web-research` заставляют проверять факты перед утверждением. Никаких выдуманных URL/версий.
- 🔁 **Самообучение** — `auto_save_skill` ловит устойчивые tool-паттерны (≥3 повторов) → черновик скилла.
- ⚡ **43 read-only команды в allow-list** + `defaultMode: auto` — никакого спама с подтверждениями.
- 🌍 **Переносимо** — нет жёстких путей, всё через env vars. Linux · macOS · WSL2.

---

## 🎯 Триггеры

Не нужно `Task(subagent_type=...)` — Claude сам выбирает специалиста по словам:

| Скажете | Сработает |
|---|---|
| «напиши / реализуй / рефактор» | `code-writer` |
| «падает / traceback / OOM» | `bug-hunter` |
| «запусти / обучи / evaluate» | `runner` (фон через nohup) |
| «прочитай статью / arxiv» | `paper-reader` |
| «исследуй / latest / какая версия» | `researcher` + `verify-claim` |
| «коммит / push» | `secret-guard` + хук блокирует |
| «запомни этот рецепт» | `record-recipe` → memory |
| «оптимизируй setup» | `self-improve` (мета-аудит) |
| «нарисуй график / matplotlib» | `data-viz` |
| «нарисуй схему / mermaid» | `diagrams` |
| «статья в латех / overleaf» | `latex-writing` |
| «найди где X / callers Y» | `smart-grep` |

**Цикл авто-фикса:**

```
тест/линтер падает  →  auto_fix_suggest читает stderr  →  grep recipes/ по regex
                  →  matching рецепт инжектится Claude  →  фикс применяется
                  →  «запомни» → record-recipe пишет файл  →  следующий раз = 0 токенов
```

---

## MLSpace / прокси

```bash
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик найдёт `HTTPS_PROXY`, замаскирует пароль в логах, прокинет в `npm config`, проверит доступность `github.com`.

> ⚠ Не вставляйте пароль в код или git — только в env vars или `~/.netrc`.

---

<details>
<summary><b>⚙️ Опциональные env vars</b></summary>

```bash
export HF_HOME=$PWD/.cache/huggingface          # кэш HuggingFace
export HARNESS_BANNED_PATHS=/home/readonly,...  # для nfs_guard hook
export GITHUB_TOKEN=ghp_...                     # для github MCP-сервера
export WANDB_DIR=$PWD/wandb                     # локальные W&B runs
```

Все необязательные — без них всё работает.

</details>

<details>
<summary><b>🔧 Кастомизация</b></summary>

```bash
# Свой скилл
mkdir -p .claude/skills/curated/мой-скилл && cat > $_/SKILL.md <<'EOF'
---
name: мой-скилл
description: Use when [триггерные фразы]. Помогает с [...]
---
EOF

# Своя slash-команда
echo 'Что показывает: !`echo привет`' > .claude/commands/foo.md   # → /foo
```

**Свой хук:** `.py` читает JSON со stdin, при блокировке печатает `{"decision":"block","reason":"..."}`. Регистрируется в `.claude/settings.json`.

**Отключить хук:** удалите его блок из `settings.json` (файл `.py` можно оставить).

</details>

<details>
<summary><b>🩺 Если что-то не работает</b></summary>

| Проблема | Решение |
|---|---|
| `claude: command not found` | `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет / < 3.10 | `apt install python3` или `brew install python` |
| `curl: (6) Could not resolve host` | DNS / прокси, см. [MLSpace](#mlspace--прокси) |
| Хук блокирует команду | `cat .claude/hooks/имя.py` чтобы понять. Чтобы отключить — переименовать `.py` |
| `secret_guard` ложно срабатывает | Добавьте в строку `# noqa: secret` |
| Обновление | `git pull && ./install.sh --target ~/harness --yes` (с бэкапом в `.bak`) |

</details>

<details>
<summary><b>❓ FAQ</b></summary>

- **Без GPU работает?** Да, `/gpu` тихо молчит если нет `nvidia-smi`.
- **Windows?** WSL2 — да, нативный — не тестировался.
- **Чем отличается от Anthropic plugin marketplace?** Маркетплейс — это каталог. `harness_bro` — готовая `.claude/` с продуманными дефолтами и установщиком в одну команду.
- **Перезапишет правки при обновлении?** Существующие файлы автобэкапятся в `<имя>.bak`. Свои новые файлы (скиллы/хуки) не конфликтуют со штатными именами.

</details>

---

<div align="center">

**[🌐 yanochka11.github.io/harness_bro](https://yanochka11.github.io/harness_bro/)** · [📦 GitHub](https://github.com/yanochka11/harness_bro) · [📜 MIT](LICENSE)

<sub>Built on top of [Claude Code](https://claude.ai/code). Skills imported from <a href="https://github.com/obra/superpowers">superpowers</a> · <a href="https://github.com/anthropics/skills">anthropic-skills</a> · <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a> · <a href="https://github.com/getsentry">sentry</a> · <a href="https://github.com/getstack">gstack</a></sub>

</div>
