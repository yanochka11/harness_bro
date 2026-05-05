# Memory index

Persistent memory across Claude Code sessions. Этот файл — индекс, не контент. Каждая запись здесь — одна строка-ссылка на отдельный файл в `recipes/` / `decisions/` / `gotchas/` / `style/`.

## Recipes (фикс-паттерны)
<!-- Каждая строка: `- [Title](recipes/file.md) — error pattern → fix in 1 line` -->

## Decisions (архитектурные решения и почему)
<!-- Каждая строка: `- [Title](decisions/file.md) — what was decided + when` -->

## Gotchas (что не работало, чего избегать)
<!-- Каждая строка: `- [Title](gotchas/file.md) — symptom → root cause` -->

## Style (пользовательские предпочтения)
<!-- Каждая строка: `- [Title](style/file.md) — what to prefer + why` -->

---

## Как пополнять

- **Авто** (через hook `auto_fix_suggest.py`): при типичной ошибке pytest/ruff/mypy hook найдёт recipe в `recipes/` и подскажет Claude'у. После успешного фикса — Claude может предложить добавить новый recipe (skill `record-recipe`).
- **Полу-авто** через skill `record-recipe`: триггер «запомни этот фикс», «save recipe» → Claude формирует frontmatter `pattern:` (regex error matching), `## Problem`, `## Fix`, `## Why`, кладёт в `recipes/<slug>.md`, добавляет строку в этот индекс.
- **Ручками** через skill `self-improve`: триггер «оптимизируй setup» → Claude анализирует skills/auto/, recipes/, предлагает promote/discard/новые скиллы.

## Schema файла рецепта

```markdown
---
name: <slug>
description: <one-liner для индекса, ≤120 chars>
type: recipe
pattern: <regex для matching ошибки в stderr/stdout, e.g. "ModuleNotFoundError.*torch">
---

## Problem
<симптом + контекст>

## Fix
<точные шаги>

## Why it works
<почему этот фикс правильный, не workaround>
```

## Schema файла gotcha

```markdown
---
name: <slug>
description: <one-liner>
type: gotcha
---

<rule>

**Why:** <случай в проекте который к этому привёл>
**How to apply:** <когда смотреть это правило>
```
