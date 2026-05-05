---
name: web-research
description: Use when needing fresh/recent/authoritative info from the internet — library docs, version numbers, benchmarks, papers, best practices, error solutions. Triggers найди в интернете, поищи, посмотри, research, что нового, latest version, current state, какая актуальная версия, best practices for, как сейчас принято делать, recent benchmarks. Provides search hierarchy, query patterns, multi-source verification.
allowed-tools: [WebSearch, WebFetch, mcp__context7__resolve-library-id, mcp__context7__query-docs, Read, Grep, Bash]
model: sonnet
---

# Web Research — методология поиска и верификации

## Когда использовать

Этот skill нужен **до того как отвечать**, если:

- Вопрос про **версию** библиотеки/инструмента (training data Claude может быть stale)
- Вопрос про **best practices** в active-development области (ML, LLMs, web frameworks)
- Вопрос про **последние** новости, релизы, статьи
- Вопрос требует **бенчмарков** или сравнений
- Вы **не уверены** в ответе (вероятность галлюцинации > 30%)
- Пользователь явно просит «найди», «посмотри», «research», «что в интернете говорят»

**Не использовать** если:
- Информация в локальном репо (читать `Read`/`Grep`, не web)
- Общий программерский вопрос (sorting, OOP) с устоявшейся теорией
- Вопрос фактологический и базовый (что такое CSV)

## Иерархия источников

Для технических вопросов всегда поднимайтесь по этой лестнице:

| Уровень | Источник | Когда |
|---|---|---|
| **0** | `context7` MCP (`/org/project`) | библиотеки/фреймворки/SDK — самая свежая дока |
| **1** | Официальный сайт vendor'а (`docs.X.com`, `learn.X.io`) | API, конфиг, syntax |
| **2** | GitHub: README, CHANGELOG, releases | версии, breaking changes, статус развития |
| **3** | arXiv / openreview / NeurIPS proceedings | research claims |
| **4** | Блог автора/maintainer'а | RFC, дизайн-решения |
| **5** | Stack Overflow с ≥10 votes и датой ≤ 2 года | конкретные ошибки |
| **6** | Reddit / HackerNews | community sentiment (не facts) |
| **7** | Random blog / Medium | use as last resort, cross-check |

**Правило**: используй ≥2 уровня для одной claim'ы. Если только Tier 6/7 — **скажи это в ответе**.

## Tool selection

```
context7 — для library docs, fresher than training cutoff
  └─ resolve-library-id "<library name>" → /org/project ID
  └─ query-docs <id> "<specific question>"

WebFetch — когда у вас есть конкретный URL
  └─ "fetch arxiv.org/abs/2401.12345 and summarize abstract+method"
  └─ "fetch github.com/X/Y/releases/latest"

WebSearch — для discovery когда не знаете URL
  └─ "<library> changelog 2026"
  └─ "<error message> site:github.com"
  └─ "<topic> arxiv 2026"

Read/Grep — если ответ в локальном проекте
  └─ перед web — всегда проверь локально
```

## Query patterns (что вводить в WebSearch)

### Версии и release
```
"<library> latest version"             ← обычно даёт changelog
"<library> 2026 release"               ← новые релизы
"<library> changelog"                  ← список изменений
site:github.com/<owner>/<repo>/releases
```

### Best practices и сравнения
```
"<topic> best practices <year>"        ← нюанс: год важен
"<X> vs <Y> <year>"                    ← сравнения
"<X> production guide"
"recommended <X> setup"
```

### Ошибки и debug
```
"<exact error message>"                ← в кавычках!
"<error>" site:github.com              ← issue tracker
"<error>" site:stackoverflow.com
"<library> <error code>"
```

### Papers
```
<topic> arxiv 2026
<topic> openreview
<paper title>                          ← для конкретной статьи
"transformer scaling laws" survey
```

### Benchmarks
```
"<model> benchmark <task>"
"<library> performance comparison <year>"
papers with code <task>
```

## Workflow

### 1. Предмет ясен → web search
```
> WebSearch "vLLM v0.7 release notes"
   → 5 results, top one is github.com/vllm-project/vllm/releases
> WebFetch <that URL>
   → returns structured release notes
```

### 2. Library specifically → context7
```
> context7 resolve-library-id "PyTorch"
   → /pytorch/pytorch
> context7 query-docs /pytorch/pytorch "how to use torch.compile with FSDP"
   → fresh code examples + caveats
```

### 3. Множественная верификация для критичной claim'ы
```
Claim: "Llama 3.1 70B беспроблемно влезает в 1× H100 80GB"

Source 1: HuggingFace model card → "model size: 140 GB FP16"  ← ❌ не влезает
Source 2: vLLM docs → "needs ≥2 GPUs at FP16, or 1 GPU at AWQ-INT4"
Source 3: Reddit thread → consistent

→ Ответ: "Не помещается в 1×H100 в FP16 (нужно ~140GB).
  С AWQ-INT4 или FP8 — да. Источники: [1][2]."
```

### 4. Synthesis с цитатами

Каждое утверждение в ответе → ссылка на источник + дата:

```markdown
**Latest stable**: vLLM v0.7.2 (released 2026-04-15) [^1].
Supports CUDA 12.4+, PyTorch 2.5+ [^1][^2].
For Llama-3 70B inference на 1×H100, AWQ-INT4 рекомендуется [^3].

[^1]: https://github.com/vllm-project/vllm/releases/tag/v0.7.2 (retrieved 2026-05-06)
[^2]: https://docs.vllm.ai/en/latest/installation.html
[^3]: https://docs.vllm.ai/en/latest/quantization/awq.html
```

## Anti-hallucination protocol

Прежде чем выдавать факт — спроси себя 3 вопроса:

1. **Знаю ли я это с уверенностью?** Если colspan между «знаю» и «возможно» — research.
2. **Может ли это быть устаревшим?** Если info > 6 месяцев в active-development области — research.
3. **Если ошибусь — насколько это плохо?** Если пользователь будет действовать на основе этого (config, install, benchmark) — research.

Если хотя бы один → research перед ответом.

### Признаки риска галлюцинации

- Версии библиотек, models, frameworks (часто меняются)
- API endpoints, query parameters, header names
- License terms (могут поменяться)
- Performance claims без числа (всегда нужны benchmarks)
- "Best practice" в новом домене (может быть устаревшее)
- Конкретные функции/методы которые я не видел в коде

### Признаки безопасного ответа без research

- Базовый CS (algorithms, data structures, OS concepts)
- Стабильные API (POSIX, HTTP basics, SQL standard)
- Локальный код проекта (читать руками)
- Историческая фактура старше 5 лет

## Format ответа

Краткий research-ответ:
```
<TL;DR в 2 строки>

Detail 1: <claim>. [^1]
Detail 2: <claim>. [^2]

Caveats: <что не смог проверить>

Sources:
[^1]: <URL> (retrieved <date>)
[^2]: <URL> (retrieved <date>)
```

Глубокий research → используй subagent `researcher` (он сам делает план + multi-source).

## Hard rules

- **Никогда не выдумывай URL.** Только URLs из реальных tool results.
- **Никогда не выдумывай arxiv ID.** Если не помнишь точно — search для верификации.
- **Никогда не давай номер версии «потому что недавно видел».** Verify через release page.
- **Всегда retrieved date** рядом с источником. Web drifts.
- **Всегда признавай несовершенство** если sources недостаточно.
- **WebFetch > WebSearch** когда URL известен (search — это router до URL).
- **Tier 1 + Tier 2** на каждую критичную claim'у.
- **Если не нашёл — скажи «не нашёл»**, а не «вот вероятный ответ».
