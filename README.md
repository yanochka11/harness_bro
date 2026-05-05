<h1 align="center">harness_bro</h1>

<p align="center">
  <b>Готовая среда Claude Code для ML/AI-инженеров.</b><br/>
  Защита от утечки ключей, постоянная память между сессиями, авто-фикс ошибок,<br/>
  90+ скиллов, 5 субагентов, 17 быстрых команд, 4 MCP-сервера.
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <img alt="Установка" src="https://img.shields.io/badge/установка-30%20секунд-brightgreen">
  <img alt="Платформа" src="https://img.shields.io/badge/платформа-linux%20%7C%20macos%20%7C%20wsl-lightgrey">
</p>

---

## 🚀 Поставить одной командой

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Скрипт сам:
1. Проверит, что у вас стоят `python ≥ 3.10`, `node`, `npm`, `git` (если чего-то нет — подскажет конкретную команду установки для вашей системы).
2. Склонирует репозиторий во временную папку.
3. Развернёт конфигурацию в `~/harness` (можно поменять флагом `--target`).
4. Сделает хуки исполняемыми и проверит сетевую доступность.

После — переходите в папку и запускайте Claude Code:

```bash
cd ~/harness
claude
```

Всё. Среда готова к работе.

---

## Что вы получаете

Голый Claude Code — это просто командная строка. Чтобы он стал реально полезным инструментом для разработки, ему нужны хуки (защита от ошибок), скиллы (знания), субагенты (специалисты), серверы MCP, память между сессиями. Поднимать всё это с нуля — несколько дней.

`harness_bro` — это та самая готовая обвязка. Один раз поставили — и всё работает.

### 🛡️ Автоматическая защита от типичных ошибок

- **Утечка API-ключей в git** — хук `secret_guard.py` блокирует любую запись в файл и `git commit` / `git push` / `git add`, если в содержимом есть ключи OpenAI, Anthropic, HuggingFace, GitHub, AWS, GCP, Slack, Stripe, W&B, приватные PEM, JWT или пароли в строках подключения к БД.
- **Запись в read-only квоты** — хук `nfs_guard.py` блокирует Write/Edit/Bash в любые пути, перечисленные в переменной `HARNESS_BANNED_PATHS`. Полезно на NFS-кластерах вроде MLSpace.
- **Битый Python** — после каждой записи `.py` файла автоматически прогоняется `AST → py_compile → ruff F-rules` (неопределённые имена, обращение до присваивания, переопределения). Сломанный код блокируется до того, как пойдёт дальше.
- **Долгие процессы в foreground** — субагент `runner` запускает обучения и эвалуации только через `nohup` с логом в `runs/<задача>/<время>/`, никогда не блокирует чат.

### 🧠 Постоянная память между сессиями

Claude больше не «забывает каждый раз». Папка `.claude/memory/` хранит:

- **Рецепты фиксов** с regex-паттернами. Когда такая же ошибка случится снова, хук `auto_fix_suggest.py` найдёт нужный рецепт и подскажет решение. Со второго раза одна и та же проблема решается мгновенно — без расхода токенов на расследование.
- **Архитектурные решения** и их причины.
- **Подводные камни** — что не работает и чего избегать.
- **Личные предпочтения** по стилю кода.

После успешного фикса достаточно сказать «запомни этот рецепт» — скилл `record-recipe` сам сформирует запись.

### 🎯 5 субагентов на триггерных фразах

Не нужно писать `Task(subagent_type=...)` — Claude сам поднимает нужного специалиста по фразам:

| Скажете | Поднимет | Что делает |
|---|---|---|
| «**напиши** / **реализуй** / **рефактор**» | `code-writer` | Читает соседние файлы, повторяет существующий стиль, валидирует AST, прогоняет тесты |
| «**падает** / **traceback** / **OOM**» | `bug-hunter` | Диагноз → 2-3 гипотезы → точечный фикс + регрессионный тест |
| «**запусти** / **обучи** / **проэвалуй**» | `runner` | Только в фоне через nohup, лог-файл, мониторинг |
| «**прочитай статью** / **arxiv**» | `paper-reader` | Структурный конспект: задача / метод / результаты / ограничения |
| «**исследуй** / **найди в интернете** / **что нового в**» | `researcher` | Многоисточниковый поиск с цитатами и датами |

### 🚫 Защита от галлюцинаций

Три скилла + субагент заставляют Claude **проверять факты** перед утверждением:

- Скилл `verify-claim` срабатывает на «latest», «какая версия», «best practices», «что нового». Перед ответом: классифицировать вопрос → найти подтверждение → честно обозначить уровень уверенности. Никаких уверенных фраз без источника.
- Скилл `web-research` — методология поиска: иерархия источников (от официальной документации до случайных блогов), шаблоны запросов, верификация по ≥2 источникам.
- Субагент `researcher` — для глубокого исследования: декомпозиция вопроса → план поиска → WebSearch + WebFetch + context7 → синтез с разделами TL;DR / Findings / Caveats / Sources.

В CLAUDE.md закреплено правило: *«Никогда не утверждай факт, в котором не уверен. Если не нашёл подтверждения — скажи "не знаю", не выдумывай.»*

### 📦 90+ скиллов из проверенных источников

Импортировано и адаптировано из `obra/superpowers`, официальных скиллов Anthropic, Hermes Agent от NousResearch, скиллов HuggingFace, Sentry, gstack:

- HuggingFace-стек (datasets, hub, trainer, gradio, papers, trackio)
- Обучение LLM (axolotl, unsloth, TRL, vLLM, llama.cpp)
- Эвалуация (lm-evaluation-harness, judge-промпты, аудит eval-пайплайнов)
- Code review и безопасность (find-bugs, code-simplifier, security-review)
- Исследовательская работа (arxiv, написание статей, structured outputs через outlines)
- Графики данных (`data-viz`: matplotlib/seaborn/plotly + принципы Tufte)
- Схемы и диаграммы (`diagrams`: Mermaid/D2/PlantUML/Excalidraw/diagrams.py)
- LaTeX-статьи и отчёты (`latex-writing`: со скелетами, Overleaf-интеграцией, исправлением частых ошибок)

### 🔁 Самообучение

- Хук `auto_save_skill.py` следит за вызовами инструментов. Если устойчивый паттерн повторился ≥3 раз (с фильтром шума) — сохраняет черновик скилла.
- Скилл `record-recipe` — после успешного фикса фиксирует решение в памяти.
- Скилл `self-improve` — мета-аудит: что накопилось, что повышать в основной набор, что выкинуть.

### ⚡ Минимум подтверждений

В `settings.json` сразу прописаны 43 разрешённые read-only команды (`rg`, `ls`, `cat`, `git status`, `nvidia-smi`, `pytest`, `ruff`, `mypy` и так далее) плюс `defaultMode: auto`. Никакого спама с подтверждениями на каждый `cat file.py`.

### 🔌 4 MCP-сервера сразу настроены

- **filesystem** — низкоуровневые файловые операции через JSON-RPC
- **github** — Issues/PR (нужен `GITHUB_TOKEN` в окружении)
- **tmux** — управление tmux-сессиями
- **context7** — свежая документация библиотек, актуальнее обучающих данных Claude

### 🌍 Переносимо

Никаких жёстко прописанных путей. Всё через переменные окружения и подстановку в шаблонах при установке. Работает на Linux, macOS, WSL2.

### 📝 17 быстрых команд

```
Код:          /lint  /format  /typecheck  /pytest  /coverage
Окружение:    /env  /gpu  /procs  /diskcfs  /hf-cache
Состояние:    /git-status  /find-todo  /last-error  /deps
              /wandb-runs  /run-dirs  /clean-tmp
```

---

## 🌐 Установка на MLSpace и за корпоративным прокси

MLSpace и большинство закрытых корпоративных серверов требуют HTTP-прокси для исходящих соединений. Чтобы установка прошла, нужно сначала экспортировать прокси.

### Шаг 1. Получите данные прокси

У администратора MLSpace или вашего IT-отдела узнайте URL прокси. Формат обычно такой:

```
http://ПОЛЬЗОВАТЕЛЬ:ПАРОЛЬ@ХОСТ:ПОРТ
```

Пример (вымышленный): `http://myuser:secret@proxy.example.com:8080`.

> ⚠ **Не вставляйте логин и пароль в код или git.** Только в переменные окружения. Лучше — в `~/.netrc` или менеджер секретов.

### Шаг 2. Экспортируйте переменные окружения

```bash
export HTTPS_PROXY="http://ПОЛЬЗОВАТЕЛЬ:ПАРОЛЬ@ХОСТ:ПОРТ"
export HTTP_PROXY="$HTTPS_PROXY"
export NO_PROXY="localhost,127.0.0.1"
```

Чтобы они работали в каждой сессии — добавьте эти три строки в `~/.bashrc` или `~/.zshrc`.

### Шаг 3. Запустите установку

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Установщик автоматически:
- найдёт `HTTPS_PROXY` / `HTTP_PROXY` и покажет адрес (пароль замаскирован)
- пропишет прокси в `npm config` (для MCP-серверов)
- проверит доступность `github.com` и предупредит, если соединение не идёт
- передаст переменные дальше в `git clone`, `pip install` и `npm install`

### Шаг 4. Проверьте, что всё установилось

```bash
cd ~/harness
ls -la .claude   # должны быть: agents/, commands/, hooks/, skills/, memory/, settings.json
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "OK"
```

### Запасной вариант — установка из локальной копии

Если `git clone` через прокси всё ещё не идёт, скачайте исходники на машине с интернетом и перенесите архивом:

```bash
# на машине с интернетом
git clone https://github.com/yanochka11/harness_bro.git
tar czf harness_bro.tgz harness_bro/

# скопируйте файл на сервер через scp / rsync, потом:
tar xzf harness_bro.tgz
cd harness_bro
./install.sh --target ~/harness --yes
```

---

## 🛠 Полная пошаговая установка

Если предпочитаете контролировать каждый шаг.

### Шаг 1. Установите зависимости

| Что | Зачем | Минимальная версия |
|---|---|---|
| `python3` | Хуки и вспомогательные скрипты | ≥ 3.10 |
| `node` + `npm` | Серверы MCP | LTS (≥ 18) |
| `git` | Клонирование, версионирование | любая |
| `claude` (Claude Code CLI) | Сама среда | актуальная |

#### Ubuntu / Debian / WSL2
```bash
sudo apt update
sudo apt install -y python3 python3-pip nodejs npm git curl
npm install -g @anthropic-ai/claude-code
```

#### macOS
```bash
brew install python node git
npm install -g @anthropic-ai/claude-code
```

#### Fedora / RHEL
```bash
sudo dnf install -y python3 python3-pip nodejs npm git
npm install -g @anthropic-ai/claude-code
```

#### Arch Linux
```bash
sudo pacman -S --needed python python-pip nodejs npm git
npm install -g @anthropic-ai/claude-code
```

Или установите Claude Code через визуальный установщик: [claude.ai/code](https://claude.ai/code).

#### Проверка
```bash
python3 --version    # должен быть ≥ 3.10
node --version       # должен быть ≥ 18
git --version
claude --version
```

### Шаг 2. Запустите установщик

#### Самый быстрый — одной командой

```bash
curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
```

Дальше — переходите к шагу 3.

#### С клоном репозитория

Если хотите изучить и поправить установщик перед запуском:

```bash
git clone https://github.com/yanochka11/harness_bro.git
cd harness_bro
./install.sh
```

Установщик задаст два вопроса:
1. **Куда поставить** — по умолчанию `~/harness`. Введите свой путь или нажмите Enter.
2. **Поставить ruff + mypy + pytest** — рекомендуется `y`, если работаете с Python.

#### В неинтерактивном режиме (CI / Docker)

```bash
./install.sh --target /opt/harness --no-tools --yes
```

Полный список флагов:

```
  --target ПУТЬ           куда поставить (по умолчанию $HOME/harness)
  --tools / --no-tools    ставить ruff/mypy/pytest или нет
  --banned-paths a,b,c    запретить запись в эти пути (через nfs_guard hook)
  --yes / -y              ничего не спрашивать, использовать значения по умолчанию
```

Переменные окружения для curl-режима:

```
  HARNESS_REPO=...        URL git-репозитория (по умолчанию официальный)
  HARNESS_BRANCH=...      ветка (по умолчанию main)
```

### Шаг 3. Перейдите в установленную папку

```bash
cd ~/harness     # или путь, который вы выбрали
```

### Шаг 4. (Необязательно) Настройте переменные окружения

В `~/.bashrc` или `~/.zshrc`:

```bash
# Кэш HuggingFace — куда скачивать модели
export HF_HOME=$PWD/.cache/huggingface

# Запретить запись в read-only пути (например, NFS-квоты)
export HARNESS_BANNED_PATHS=/home/readonly,/mnt/quota

# Для GitHub MCP-сервера
export GITHUB_TOKEN=ghp_ваш_токен

# Если будете обучать модели:
export WANDB_DIR=$PWD/wandb
export TORCH_HOME=$PWD/.cache/torch
export TRITON_CACHE_DIR=$PWD/.cache/triton
```

Все переменные **необязательные**. Без них всё работает, просто несколько функций отключены (например, `nfs_guard` ничего не блокирует, если `HARNESS_BANNED_PATHS` пуст).

### Шаг 5. Запустите Claude Code

```bash
claude
```

Готово. Вы внутри настроенной среды.

### Шаг 6. (Опционально) Базовая проверка

Убедитесь что всё на месте:
```bash
ls -la ~/harness/.claude   # agents, commands, hooks, skills, memory, settings.json
python3 -c "import json; json.load(open('$HOME/harness/.claude/settings.json')); print('ok')"
```

---

## 🎬 Первая сессия

Запустили `claude` — попробуйте быстрые команды:

```
/env             ← покажет conda, python, HF_HOME, токены, GPU
/gpu             ← снимок nvidia-smi
/git-status      ← состояние репозитория, если он есть
```

Дальше попросите что-нибудь сделать:

```
> напиши простой fastapi-эндпоинт в hello.py с health-check
```

Claude автоматически поднимет субагент `code-writer` (по слову «напиши»), прочитает соседние файлы (если есть), напишет `hello.py`, прогонит AST-валидацию через хук `validate_python.py`. Если код кривой — увидит ошибку и сам исправит.

Попробуйте поломать что-нибудь:

```
> запусти pytest
```

Если упадёт с `ModuleNotFoundError: torch` — хук `auto_fix_suggest.py` найдёт подходящий рецепт в `.claude/memory/recipes/` и предложит решение.

После того как фикс сработал:

```
> запомни этот рецепт
```

Скилл `record-recipe` сформирует новый файл в `.claude/memory/recipes/` с регулярным выражением для матчинга. В следующий раз эта же ошибка решится автоматически.

---

## 📦 Что внутри

```
.claude/
├── agents/          5 субагентов: bug-hunter, code-writer, runner, paper-reader, researcher
├── commands/        17 быстрых команд (read-only снимки)
├── hooks/           6 хуков: nfs_guard, secret_guard, validate_python,
│                    auto_save_skill, auto_fix_suggest, statusline
├── skills/
│   ├── curated/     46 — отобранные (workflow, evals, gstack, мета, безопасность,
│   │                latex-writing, data-viz, diagrams, web-research, verify-claim)
│   └── ported/      53 — импорт из Hermes / Anthropic / HuggingFace / Sentry
├── memory/          Постоянная память между сессиями
│   ├── MEMORY.md    Индекс
│   ├── recipes/     Рецепты фиксов (с regex pattern: для auto_fix_suggest hook)
│   ├── decisions/   Архитектурные решения
│   ├── gotchas/     Чего избегать
│   └── style/       Личные предпочтения
└── settings.json    Регистрация хуков и разрешения
```

Корневые файлы после установки:

```
~/harness/
├── .claude/         (см. выше)
├── .gitignore       секреты, артефакты обучения, состояние Claude
├── .mcp.json        4 MCP-сервера: filesystem, github, tmux, context7
├── CLAUDE.md        что Claude читает в начале каждой сессии
├── README.md        этот файл
└── LICENSE          MIT
```

---

## 🎯 Как этим пользоваться

### Триггерные фразы

| Скажете | Сработает |
|---|---|
| «напиши / реализуй / рефактор» | `code-writer` agent |
| «падает / traceback / OOM» | `bug-hunter` agent |
| «запусти / обучи / проэвалуй» | `runner` agent (фон) |
| «прочитай статью / arxiv 2401.12345» | `paper-reader` agent |
| «исследуй / найди в интернете / latest version» | `researcher` agent |
| «коммит / push» | `secret-guard` skill + хук автоматически |
| «запомни этот рецепт» | `record-recipe` skill → память |
| «оптимизируй setup / что улучшить» | `self-improve` skill |
| «нарисуй график / chart / matplotlib» | `data-viz` skill |
| «нарисуй схему / диаграмма / mermaid» | `diagrams` skill |
| «напиши статью в латех / overleaf» | `latex-writing` skill |
| «найди где X / callers Y» | `smart-grep` skill |

### Автофикс-цикл

```
Тест или линтер падает
   ↓
auto_fix_suggest hook читает stderr
   ↓
ищет matching recipe в memory/recipes/ по regex
   ↓
нашёл — рецепт показывается Claude
   ↓
Claude применяет фикс
   ↓
вы говорите «запомни» → record-recipe пишет новый файл
   ↓
в следующий раз эта же ошибка решается автоматически
```

### Защита секретов (4 уровня)

```
1. Хук secret_guard.py     — блокирует Write/Edit/git с ключами на уровне Claude Code
2. .gitignore              — .env*, *.key, *.pem, credentials.json никогда не попадают в git
3. Скилл secret-guard      — Claude знает процедуру: отозвать ключ, переписать историю
4. (опционально) pre-commit + gitleaks + detect-secrets если используете git-хуки
```

---

## 🔧 Кастомизация

### Добавить свой скилл

```bash
mkdir -p .claude/skills/curated/мой-скилл
cat > .claude/skills/curated/мой-скилл/SKILL.md <<'EOF'
---
name: мой-скилл
description: Use when [триггерные фразы]. Помогает с [...]
---

# Тело скилла — Claude грузит только если description совпадает с запросом
EOF
```

### Добавить быструю команду

```bash
cat > .claude/commands/foo.md <<'EOF'
Что показывает эта команда:
!`bash -c 'echo привет'`
EOF
```

Сразу доступна как `/foo`.

### Добавить субагент

`.claude/agents/мой-агент.md`:

```markdown
---
name: мой-агент
description: Use when [фразы]. [Что делает в одном предложении]
tools: [Read, Write, Edit, Bash, Grep, Glob]
model: sonnet
---

Вы — [роль]. [Системный промпт].
```

### Добавить хук

`.claude/hooks/мой_хук.py` — читает JSON со stdin:

```python
import json, sys
data = json.load(sys.stdin)
# event = data["hook_event_name"]
# tool  = data.get("tool_name")
# Чтобы заблокировать: print(json.dumps({"decision":"block","reason":"почему"}))
sys.exit(0)
```

Зарегистрируйте в `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/мой_хук.py"
      }]
    }]
  }
}
```

### Отключить хук

Удалите его блок из секции `hooks` в `.claude/settings.json`. Файл `.py` можно оставить — без регистрации хук не запускается.

---

## 🩺 Если что-то не работает

| Проблема | Решение |
|---|---|
| `claude: command not found` после `npm install -g` | Добавьте папку с глобальными npm-бинарниками в `PATH`: `export PATH=$PATH:$(npm config get prefix)/bin` |
| `python3` нет или версия младше 3.10 | Поставьте Python ≥ 3.10 (см. [шаг 1](#шаг-1-установите-зависимости)) |
| `curl: (6) Could not resolve host` | Проблема с DNS или прокси. Экспортируйте `HTTPS_PROXY` (см. секцию [MLSpace](#-установка-на-mlspace-и-за-корпоративным-прокси)) |
| `npm install` через прокси зависает | `npm config set proxy $HTTPS_PROXY && npm config set https-proxy $HTTPS_PROXY` (установщик делает это сам, если переменные выставлены) |
| `install.sh` падает на NFS | Запустите с `bash -x install.sh ...` — увидите конкретный шаг |
| Хук блокирует команду, которую вы хотели запустить | Посмотрите код хука: `cat .claude/hooks/имя.py`. Можно временно отключить — переименовать файл, и хук перестанет запускаться |
| `secret_guard` ловит ложное срабатывание в тестовой фикстуре | Добавьте в строку `# noqa: secret` |
| `auto_save_skill` копит мусор | Уже отфильтровано (whitelist tools, ≥3 повторов, bash-сигнал). Если всё равно лишнее — поправьте `BASH_SIGNALS` в `.claude/hooks/auto_save_skill.py` |
| `/gpu` ничего не показывает | Это нормально, если на машине нет `nvidia-smi`. Хук `statusline.sh` пропускает GPU-секцию автоматически |
| Хочу убедиться что хук работает | Прогоните вручную: `echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/tmp/x.py","content":"k=\"sk-..."}}' \| python3 .claude/hooks/secret_guard.py` |
| Хочу обновить harness_bro | `cd harness_bro && git pull && ./install.sh --target существующая_папка --yes` (установщик идемпотентный, делает `.bak` копии) |

---

## ❓ Частые вопросы

**Можно ли использовать без GPU?**
Да. `/gpu` корректно молчит, если `nvidia-smi` отсутствует. Скиллы для ML ничего не ломают, если их не вызывать.

**Будет ли работать на Windows?**
WSL2 — да. Нативный Windows — не тестировался (хуки на bash и Python).

**Чем это отличается от маркетплейса плагинов Anthropic?**
Маркетплейс — это каталог плагинов. `harness_bro` — это **готовая `.claude/` конфигурация**: продуманные значения по умолчанию, готовые хуки, отобранный набор скиллов, установщик в одну команду.

**Можно ли использовать только часть функций?**
Да. Удалите ненужные хуки из `.claude/settings.json`. Удалите ненужные скиллы из `.claude/skills/`. Установщик идемпотентный, можно перезапускать.

**Перезапишет ли установщик мои правки?**
Существующие файлы автоматически копируются в `<имя>.bak` (один раз). Так что правки не теряются — но новый запуск `install.sh` всё равно перезапишет основной файл. Для постоянных кастомизаций добавляйте свои файлы (новые скиллы, хуки, команды) — они не конфликтуют со штатными именами.

**Как увидеть, как это выглядит в работе?**
Запустите `/env` сразу после первой сессии. Затем попробуйте «напиши простой скрипт X». Через 30 секунд увидите, как `code-writer` agent читает файлы, пишет код, проводит валидацию.

---

## 🤝 Участие в разработке

Pull Request-ы приветствуются. Особенно:

- 🪝 Новые хуки (со smoke-тестом в описании PR)
- 📝 Новые скиллы (с triggers в `description:` frontmatter)
- 📚 Рецепты типичных ошибок в `.claude/memory/recipes/`
- 🐛 Багфиксы установщика на разных дистрибутивах
- 🌍 Переводы

**Стиль кода:**
- Хуки: Python ≥ 3.10, type-аннотации, без внешних зависимостей сверх stdlib
- Скиллы: SKILL.md с триггерными фразами в `description:`
- Bash: `set -euo pipefail`, кавычки на переменных, массивы вместо разбиения по пробелу

---

## 📜 Лицензия

MIT — см. файл [LICENSE](LICENSE).

Импортированные скиллы сохраняют лицензии исходных проектов (все MIT).

---

## 🙏 Благодарности

Построено поверх [Claude Code](https://claude.ai/code) от Anthropic.

Источники скиллов:
- [obra/superpowers](https://github.com/obra/superpowers) — паттерны рабочих процессов
- [anthropics/skills](https://github.com/anthropics/skills) — официальные скиллы
- [NousResearch/Hermes Agent](https://github.com/NousResearch/hermes-agent) — MLOps и dev-скиллы
- [getsentry skills](https://github.com/getsentry) — скиллы для отладки
- [getstack/gstack](https://github.com/getstack) — методология отладки
