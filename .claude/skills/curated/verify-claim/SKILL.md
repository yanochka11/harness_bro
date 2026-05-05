---
name: verify-claim
description: Use BEFORE asserting any fact you're not 100% certain about. Anti-hallucination protocol. Triggers latest, recent, current, какая версия, что нового в, как сейчас принято, в новой версии X, best practice, supported, deprecated, when did, кто автор, on which date, statistics, benchmark numbers, license terms. Forces grounding via Read for code, web-research/researcher for external facts.
allowed-tools: [Read, Grep, Glob, WebSearch, WebFetch, mcp__context7__resolve-library-id, mcp__context7__query-docs]
model: sonnet
---

# Verify-Claim — anti-hallucination protocol

Этот skill предотвращает самую частую failure-mode LLM: **выдавать confident-sounding ответ на вопрос про который не знаешь**.

## Iron rule

**Никогда не утверждай факт о котором не уверен. Сначала проверь, потом скажи.**

Anthropic's official guidance: *"Never make any claims about code before investigating unless you are certain of the correct answer — give grounded and hallucination-free answers."*

## Когда срабатывает

Любая из следующих ситуаций:

### Категория 1 — про код пользователя
- Пользователь упоминает файл/функцию/класс — **прочитай файл** перед ответом.
- Пользователь спрашивает «как у меня сделано X» — **grep** перед ответом.
- Пользователь предполагает что в проекте есть Y — **проверь**, не предполагай.

### Категория 2 — про внешние факты с risk галлюцинации
- Версии библиотек, фреймворков, OS, моделей
- API endpoints, query parameters, конфиги
- License terms, depreциация, breaking changes
- Performance/benchmark numbers без источника
- arxiv ID, paper authors, конкретные числа из papers
- Конкретные методы/функции которых вы не видели в свежей доке
- "Best practice" в области с быстрым развитием (LLM, web frameworks, ML libs)
- Дата релиза / event'а

### Категория 3 — uncertainty signals
Если в вашем «черновом ответе» есть хедж-слова — это signal проверить:
- «Я думаю...», «Скорее всего...», «Кажется...», «Возможно...»
- «Обычно X делает...», «По умолчанию...»
- «В версии 3 это работает так...» (а вы не уверены что это v3)
- «Хороший подход — ...» (без источника)

## Protocol

### Шаг 1 — STOP и классифицировать

Прежде чем напечатать ответ — спроси:

```
1. Это про локальный код?     → Read/Grep
2. Это про библиотеку/SDK?    → context7 → WebFetch officials
3. Это про recent news/release? → WebSearch
4. Это про academic paper?    → WebFetch arxiv
5. Я уверен на 100%?          → если нет, см. 1-4
```

### Шаг 2 — Найти ground truth

| Тип claim'ы | Где проверять |
|---|---|
| Существование функции/файла в проекте | `Glob`, `Grep`, `Read` |
| Версия библиотеки | `WebFetch <github>/releases/latest` или `pip show X` |
| API библиотеки | `context7 query-docs /org/lib "<question>"` |
| Best practice | `WebSearch "<topic> best practices <year>"` + ≥2 источника |
| Bug в библиотеке | `WebSearch "<error>" site:github.com` |
| Paper-claim | `WebFetch arxiv.org/abs/<id>` (verify ID first!) |
| Recent event | `WebSearch "<event> <year>"` |
| License | `WebFetch <repo>/blob/main/LICENSE` |

Для глубокого research — делегируй subagent `researcher`.

### Шаг 3 — Honest framing в ответе

Структура зависит от уверенности:

#### Если проверил и точно знаешь
```
<факт>. [Source: <URL>, retrieved <date>]
```

#### Если проверил частично
```
<факт> — based on <source>. Couldn't verify <specific aspect>;
recommend checking <where to verify>.
```

#### Если **не смог** проверить
```
Я не уверен. Я нашёл [...], но не могу подтвердить
[конкретно что]. Рекомендую: <как пользователь может это проверить>.
```

#### Если знаю что моё training data может быть stale
```
По данным на момент моего обучения — <X>. Это могло измениться;
для актуальной info: <ссылка>.
```

## Common hallucination traps (избегать)

### 1. Confident version numbers
❌ "Latest version of vLLM is 0.6.5"
✅ "Latest version I'm aware of is 0.6.5 (from training cutoff). Check https://github.com/vllm-project/vllm/releases for current."

### 2. Phantom function/method names
❌ "Use `torch.compile_with_amp(model)`"  ← может не существовать
✅ Сначала `context7 query-docs /pytorch/pytorch "how to combine torch.compile with mixed precision"` → use real API.

### 3. Fake citations
❌ "According to Smith et al. 2023, transformer attention scales O(n²)..." ← фабрикация
✅ Если упоминаете paper — `WebFetch` его abstract или скажите «согласно общепринятому...».

### 4. Phantom API endpoints
❌ "POST /api/v3/users/{id}/posts" ← придумано
✅ Проверить в OpenAPI spec / docs / actual repo code.

### 5. Confidently wrong defaults
❌ "В Postgres `max_connections` по умолчанию 1000"
✅ `WebFetch postgresql.org/docs/current/runtime-config-connection.html` → real default 100.

### 6. Inventing what's "deprecated"
❌ "Метод X deprecated в TensorFlow 2.10" ← может быть, может нет
✅ Проверить changelog или skip claim.

## When to refuse vs research

| Сценарий | Действие |
|---|---|
| Простой verifiable factoid (версия) | research → answer |
| Нужны 3+ источников для синтеза | спросить «нужен ли deep research?» → invoke `researcher` agent |
| Полностью obscure topic | прямо сказать «обскура, могу галлюцинировать, давайте искать вместе» |
| Пользователь хочет «быстрый ответ» а вы не знаете | **сказать что не знаете** — лучше чем галлюцинировать |
| Critical decision (security, prod) | force-research, не отвечать на память |

## Hard rules

- **Никогда не утверждайте версию/число/дату не проверив.**
- **Никогда не цитируйте paper не открыв его** (или не имея precise memory + source).
- **Никогда не выдумывайте URL.** URL только из tool results.
- **Признавайте «не знаю»** — это знак силы, не слабости.
- **При риске — research.** Несколько секунд WebFetch лучше чем confidently wrong ответ.
- **Перед коммитом фикса** — проверьте что фикс работает на real code (Read/run tests), а не на воображаемом.

## Quick checklist перед ответом

Прежде чем нажать enter:

```
[ ] Если это про код в репо — я прочитал нужные файлы?
[ ] Если это про внешний факт — у меня есть source link?
[ ] Если есть число/версия/дата — оно из verified источника?
[ ] Если я hedge'аю («скорее всего») — не должен ли я сначала проверить?
[ ] Если я не уверен на 80%+ — я об этом сказал?
```

Если хоть на один **нет** — STOP, research, потом отвечай.

## Связанные

- **`web-research`** skill — методология поиска (когда `verify-claim` говорит «надо research»).
- **`researcher`** subagent — для multi-step deep research с синтезом.
- **`smart-grep`** skill — для locating fact'ов внутри local code.
- **`systematic-debugging`** skill — для root-cause investigation вместо guess.
