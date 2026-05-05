---
name: self-improve
description: Use when user asks "оптимизируй setup", "что улучшить", "audit my claude config", "что я могу автоматизировать", "refactor my workflow", "добавь скилл", "что нового можно сделать". Аудит .claude/ и предложения по promotе draft-скиллов, удалению шума, созданию новых артефактов.
allowed-tools: [Read, Bash, Grep, Glob]
model: sonnet
---

# Self-Improve — мета-скилл аудита Claude Code setup'а

Задача: периодически (или по запросу) проверять что накопилось в `.claude/` и предлагать **конкретные** действия, а не общие советы.

## Источники сигнала

| Где | Что искать |
|---|---|
| `.claude/skills/auto/` | Auto-captured драфты от `auto_save_skill.py`. Имена `auto-X-Y-Z-<ts>/`. Это устойчивые tool-тройки (≥3 повторов, ≥3 уникальных tool, есть bash-сигнал). Кандидаты на promote. |
| `.claude/memory/recipes/` | Записанные фикс-рецепты. Если ≥10 рецептов на одну тему (e.g. CUDA OOM) — пора создать **скилл** автоматизирующий весь процесс, а не отдельные рецепты. |
| `.claude/state/tool_trace.jsonl` | Сырая статистика tool calls. Грепом найти топ-10 bash-команд — кандидаты на новую slash-команду. |
| `.claude/skills/auto/` старее 14 дней | Пыль. Удалить. |
| `cleanup.sh` dry-run | Сколько мусора накопилось. |

## Workflow

### 1. Сбор статистики

```bash
echo "── auto drafts ──"
ls -lt $ALPHA_ROOT/.claude/skills/auto/ 2>/dev/null

echo "── recipes ──"
ls $ALPHA_ROOT/.claude/memory/recipes/

echo "── topcommands в trace (если файл свежий) ──"
test -f $ALPHA_ROOT/.claude/state/tool_trace.jsonl && \
  python3 -c "
import json
from collections import Counter
c = Counter()
for line in open('$ALPHA_ROOT/.claude/state/tool_trace.jsonl'):
    try:
        e = json.loads(line)
        if e.get('tool') == 'Bash':
            cmd = e.get('input_preview','')[:60]
            c[cmd] += 1
    except: pass
for cmd, n in c.most_common(10):
    print(f'{n:>3}  {cmd}')
"

echo "── inventory ──"
bash $ALPHA_ROOT/inventory.sh | tail -10

echo "── cleanup dry-run ──"
bash $ALPHA_ROOT/cleanup.sh
```

### 2. Анализ и рекомендации

| Симптом | Действие |
|---|---|
| Auto-draft `auto-read-edit-bash-…` встретился 5 раз | Promote: переименовать в `iterative-fix`, описать триггеры, перенести в `curated/`. |
| 8+ recipe-файлов про разные CUDA-ошибки | Создать новый skill `cuda-debug` с workflow вместо отдельных рецептов. |
| Та же bash-команда `nvidia-smi --query…` в топе 30+ раз | Уже есть `/gpu`? Если нет — создать. Если да — упомянуть пользователю. |
| Drafts старше 14 дней | `rm -rf .claude/skills/auto/auto-…` (или дождаться cleanup.sh). |
| `cleanup.sh dry-run` показал >100 MB | Запустить `cleanup.sh --force` (или `--aggressive` если runs >30д). |
| MEMORY.md пуст, но есть старые recipes | Регенерировать индекс (можно скриптом). |

### 3. Output (для пользователя)

Структурированный список **конкретных** команд:

```
## Найдено

### Promote candidates (auto-skills повторившиеся ≥3 раз)
1. auto-edit-bash-read-20260506-... (8 раз) →
   mv .claude/skills/auto/auto-... .claude/skills/curated/iterative-fix/
   и отредактировать SKILL.md (description с триггерами).

### Удалить шум
- .claude/skills/auto/auto-... (старее 14 дней)

### Создать новый skill
- skill `cuda-oom-debug` — у тебя 6 рецептов по CUDA OOM. Объединить в workflow.

### Запустить
- bash $ALPHA_ROOT/cleanup.sh --force  # 84 MB к удалению
```

## Hard rules

- **Ничего не делай без подтверждения** — это аудиторский скилл, а не deletor.
- Не предлагай удалять curated/ или ported/ скиллы. Только auto/.
- Не предлагай удалять hermes_root/, .conda/, .npm-global/ — это не setup-мусор.
- Promote = ручное действие через mv + правка SKILL.md, не автоматическое.
- Если ничего не накопилось — честно сказать «нет рекомендаций, setup в порядке».
