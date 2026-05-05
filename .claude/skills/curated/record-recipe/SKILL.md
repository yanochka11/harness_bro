---
name: record-recipe
description: Use AFTER successful fix to save it for next time. Triggers запомни как фиксили, сохрани рецепт, this fix worked, save recipe, добавь в память, save to memory, remember this fix. Кладёт SKILL.md-стиль recipe в .claude/memory/recipes/ + обновляет MEMORY.md.
allowed-tools: [Read, Write, Edit, Grep, Glob]
model: sonnet
---

# Record Recipe — закрепить успешный фикс в memory

Когда какой-то фикс наконец сработал — записать в `.claude/memory/recipes/<slug>.md` чтобы:
1. В будущем `auto_fix_suggest.py` hook найдёт regex-pattern в выводе ошибки и автоматически подскажет рецепт.
2. Не повторять отладку.

## Когда

Триггеры от пользователя: «запомни», «сохрани рецепт», «save recipe», «remember this fix».

Также можно **проактивно** предложить запись recipe если:
- Только что был нетривиальный фикс (≥3 шага).
- Ошибка имеет узнаваемый pattern (не "что-то сломалось").
- Это не одноразовый случай (вероятность повторения).

## Что записать

Файл `.claude/memory/recipes/<slug>.md`:

```markdown
---
name: <slug-with-dashes>
description: <одна строка ≤120 chars — error pattern → fix>
type: recipe
pattern: <regex для re.search по stderr/stdout — используется auto_fix_suggest hook'ом>
---

## Problem
<симптом + контекст: какая команда падает, какое сообщение>

## Fix
<точные шаги — команды, edits, ссылки на файлы>

## Why it works
<почему этот фикс корректный, не workaround. Что было корнем проблемы.>
```

### Pattern field — критично

Это **regex** (Python `re.search`) для matching против stderr/stdout. Примеры:
- `ModuleNotFoundError.*torch` — torch не установлен в env
- `RuntimeError:.*CUDA out of memory` — OOM
- `F821.*Undefined name` — ruff F821
- `gitleaks.*found secrets` — gitleaks alert

Не делать pattern слишком общим (`Error`) — будет ловить что попало. И не слишком специфичным (`F821 Undefined name 'foo' on line 42` с буквальным именем) — будет ловить только этот конкретный случай.

## Workflow

1. **Прочитать** существующие `.claude/memory/recipes/*.md` — нет ли уже такого pattern.
2. **Сформировать** content:
   - slug = `<topic>-<key-detail>` (например `torch-modulenotfound`, `cuda-oom-bs`, `ruff-f821-import-cycle`).
   - description = краткое описание для индекса.
   - pattern = regex.
   - body = Problem / Fix / Why.
3. **Write** файл в `.claude/memory/recipes/<slug>.md`.
4. **Append** строку в `.claude/memory/MEMORY.md`:
   ```
   - [<slug>](recipes/<slug>.md) — <one-line hook>
   ```
   Под секцией `## Recipes`.
5. Подтвердить пользователю: «записан рецепт `<slug>`, hook auto_fix_suggest подхватит его при следующей такой ошибке».

## Quality bar

Не сохранять recipe если:
- Фикс — это `pip install <библиотека>` (тривиально, не recipe).
- Симптом одноразовый («у меня моргнул сервак»).
- Фикс — workaround а не root-cause (тогда — gotcha, не recipe).

Лучше 5 хороших recipes чем 50 плохих.

## Связанные скиллы

- `self-improve` — анализирует накопленные recipes и предлагает создать новый skill если их слишком много по одной теме.
- `systematic-debugging` (curated) — методология которая ведёт к recipe-достойным фиксам.
