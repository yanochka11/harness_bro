<h1 align="center">harness_bro</h1>

<p align="center">
  <b>Готовая среда Claude Code для ML/AI-инженеров.</b><br/>
  Защита от утечки ключей · постоянная память · авто-фикс ошибок · 99 скиллов · 5 субагентов · 17 команд · 4 MCP-сервера
</p>

<p align="center">
  <a href="https://yanochka11.github.io/harness_bro/"><img alt="Site" src="https://img.shields.io/badge/site-yanochka11.github.io-1f6feb"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-yellow.svg"></a>
  <img alt="Установка" src="https://img.shields.io/badge/установка-30%20секунд-brightgreen">
  <img alt="Платформа" src="https://img.shields.io/badge/linux%20%7C%20macos%20%7C%20wsl-lightgrey">
</p>

---

## 🚀 Поставить одной командой

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Скрипт сам проверит зависимости (`python ≥ 3.10`, `node`, `npm`, `git`), склонирует репо во временную папку, развернёт конфиг в `~/harness`, сделает хуки исполняемыми. Идемпотентный — можно перезапускать.

После — `cd ~/harness && claude`. Готово.

**Флаги** (опционально, через `bash -s --`):
```
--target <путь>          куда поставить (по умолчанию ~/harness)
--tools / --no-tools     ставить ли ruff/mypy/pytest
--banned-paths a,b,c     запрет записи в эти пути (используется hook nfs_guard)
--yes                    ничего не спрашивать
```

**Сайт-презентация:** https://yanochka11.github.io/harness_bro/

---

## 🌐 На MLSpace и за прокси

Получите URL прокси у админа и экспортируйте перед установкой:

```bash
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик найдёт `HTTPS_PROXY`, замаскирует пароль в выводе, прокинет в `npm config`, проверит доступность `github.com`. Если соединение не идёт — выдаст подсказку.

> ⚠ Не вставляйте пароль в код или git. Только в env vars или `~/.netrc`.

---

## 📦 Что внутри

| Слой | Чем рулит |
|---|---|
| **5 субагентов** | `bug-hunter` · `code-writer` · `runner` · `paper-reader` · `researcher` |
| **6 хуков** | `nfs_guard` · `secret_guard` · `validate_python` · `auto_save_skill` · `auto_fix_suggest` · `statusline` |
| **17 быстрых команд** | `/lint /format /typecheck /pytest /coverage` · `/env /gpu /procs /diskcfs /hf-cache` · `/git-status /find-todo /last-error /deps /wandb-runs /run-dirs /clean-tmp` |
| **99 скиллов** | 46 curated (workflow, evals, gstack, latex, data-viz, diagrams, secret-guard, self-improve, web-research, verify-claim) + 53 ported (HuggingFace, axolotl/unsloth/TRL, vLLM, llama.cpp, lm-eval-harness, code-review, github, arxiv, dspy, outlines) |
| **4 MCP-сервера** | `filesystem` · `github` · `tmux` · `context7` (свежая документация библиотек) |
| **Память** | `MEMORY.md` + `recipes/` (с regex pattern для auto_fix_suggest) + `decisions/` + `gotchas/` + `style/` |

### Ключевые фишки

- 🛡️ **Защита от утечки секретов на 4 уровнях** — хук блокирует Write/Edit/git-commit с ключами OpenAI, Anthropic, HuggingFace, GitHub PAT, AWS, GCP, Slack, Stripe, W&B, JWT, PEM, DB-strings.
- 🧠 **Постоянная память между сессиями** — успешный фикс с regex-паттерном кладётся в `recipes/`. В следующий раз эта же ошибка решается мгновенно через `auto_fix_suggest` hook.
- 🚫 **Anti-hallucination** — скилл `verify-claim` срабатывает на «latest», «какая версия», «best practices» и заставляет проверить факт. `web-research` даёт методологию поиска. Никаких выдуманных URL/версий.
- 🔁 **Самообучение** — `auto_save_skill` ловит устойчивые tool-паттерны (≥3 повторов с фильтром шума) → черновик скилла.
- ⚡ **Минимум подтверждений** — 43 read-only команды в allow-list + `defaultMode: auto`.
- 🌍 **Переносимо** — нет жёстко прописанных путей, всё через env vars.

---

## 🎯 Триггерные фразы

Не нужно `Task(subagent_type=...)` — Claude сам поднимает специалиста по словам в сообщении:

| Скажете | Сработает |
|---|---|
| «напиши / реализуй / рефактор» | `code-writer` |
| «падает / traceback / OOM» | `bug-hunter` |
| «запусти / обучи / evaluate» | `runner` (фон через nohup) |
| «прочитай статью / arxiv 2401.x» | `paper-reader` |
| «исследуй / latest / какая версия» | `researcher` + `verify-claim` |
| «коммит / push» | `secret-guard` + хук блокирует |
| «запомни этот рецепт» | `record-recipe` → memory |
| «оптимизируй setup» | `self-improve` (мета-аудит) |
| «нарисуй график / matplotlib» | `data-viz` |
| «нарисуй схему / mermaid» | `diagrams` |
| «статья в латех / overleaf» | `latex-writing` |
| «найди где X / callers Y» | `smart-grep` |

### Цикл авто-фикса

```
тест/линтер падает → auto_fix_suggest читает stderr → grep recipes/ по regex →
matching рецепт инжектится в stderr → Claude применяет фикс →
вы говорите «запомни» → record-recipe пишет новый файл → следующий раз = 0 токенов
```

---

## ⚙️ Переменные окружения (опционально)

Все необязательные. Без них всё работает.

```bash
export HF_HOME=$PWD/.cache/huggingface          # кэш HuggingFace
export HARNESS_BANNED_PATHS=/home/readonly,...  # для nfs_guard hook
export GITHUB_TOKEN=ghp_...                     # для github MCP-сервера
export WANDB_DIR=$PWD/wandb                     # локальные W&B runs
```

---

## 🔧 Кастомизация

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

# Свой хук — .py читает JSON со stdin, при блокировке печатает
# {"decision":"block","reason":"..."}, регистрируется в .claude/settings.json
```

Отключить хук — удалите его блок из `.claude/settings.json` (файл .py можно оставить).

---

## 🩺 Если что-то не работает

| Проблема | Решение |
|---|---|
| `claude: command not found` | `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет или < 3.10 | `apt install python3` / `brew install python` |
| `curl: (6) Could not resolve host` | DNS / прокси, см. секцию [MLSpace](#-на-mlspace-и-за-прокси) |
| Хук блокирует команду | Просмотрите `cat .claude/hooks/имя.py`. Чтобы временно отключить — переименуйте файл |
| `secret_guard` ловит false-positive | Добавьте в строку `# noqa: secret` |
| Хочу обновиться | `cd harness_bro && git pull && ./install.sh --target ~/harness --yes` |

---

## ❓ FAQ

**Без GPU работает?** Да, `/gpu` молчит если `nvidia-smi` нет.

**Windows?** WSL2 — да, нативный — не тестировался.

**Чем отличается от Anthropic plugin marketplace?** Маркетплейс — каталог плагинов. `harness_bro` — готовая `.claude/` с продуманными дефолтами и установщиком в одну команду.

**Перезапишет мои правки при обновлении?** Существующие файлы автоматически бэкапятся в `<имя>.bak`. Свои новые файлы (скиллы/хуки/команды) не конфликтуют со штатными именами.

---

## 📜 Лицензия

MIT — см. [LICENSE](LICENSE). Импортированные скиллы сохраняют свои MIT-лицензии.

---

## 🙏 Источники

Построено поверх [Claude Code](https://claude.ai/code) (Anthropic). Скиллы из:
[obra/superpowers](https://github.com/obra/superpowers) ·
[anthropics/skills](https://github.com/anthropics/skills) ·
[NousResearch/Hermes Agent](https://github.com/NousResearch/hermes-agent) ·
[getsentry skills](https://github.com/getsentry) ·
[getstack/gstack](https://github.com/getstack)
