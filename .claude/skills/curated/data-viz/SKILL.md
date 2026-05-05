---
name: data-viz
description: Use when plotting data — exploration, papers, dashboards, reports. Triggers нарисуй график, plot, chart, графики, визуализация данных, matplotlib, seaborn, plotly, EDA charts, dashboard, для статьи график. Picks library by use case (matplotlib for static control, seaborn for stats EDA, plotly for interactive). Applies design principles (Tufte, accessible palettes).
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
model: sonnet
---

# Data Viz — графики данных

## Library selection

Выбор за 1 секунду:

| Use case | Library | Когда |
|---|---|---|
| **Полный контроль** (paper figure, кастомный layout) | matplotlib | подгонка под NeurIPS template, multi-panel composition |
| **Быстрая стат-разведка** (EDA) | seaborn | distributions, pairplot, heatmaps, jointplots |
| **Интерактивный** (dashboard, Jupyter) | plotly | hover, zoom, pan, на сайт |
| **Production export** (PNG/PDF) | matplotlib | финальные figures для статьи или отчёта |
| **Декларативный + composable** (Vega/Altair) | altair | grammar of graphics, JSON-spec |

Правило: для одного проекта обычно используют **2 библиотеки** — seaborn для exploration, matplotlib для финального polish.

## Скелет (matplotlib + seaborn)

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Глобальный стиль — один раз в начале
sns.set_theme(
    style="whitegrid",        # whitegrid | white | darkgrid | dark | ticks
    context="paper",          # paper | notebook | talk | poster (= размер шрифтов)
    palette="colorblind",     # accessible палитра по умолчанию
)
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.family": "serif",   # для статей
    "axes.spines.right": False,
    "axes.spines.top": False,
})

# 2. Всегда явный fig/ax (не plt.plot напрямую)
fig, ax = plt.subplots(figsize=(6, 4))
sns.lineplot(data=df, x="step", y="loss", hue="variant", ax=ax)
ax.set_xlabel("Training step")
ax.set_ylabel("Loss")
ax.set_title("")  # часто title в caption статьи, не на figure
ax.legend(title="", loc="best", frameon=False)

# 3. Tight layout + save
fig.tight_layout()
fig.savefig("figures/loss.pdf", bbox_inches="tight")
plt.close(fig)  # важно в loop'ах — иначе утечка памяти
```

**PDF, не PNG** для статей/латеха (vector → масштабируется).

## Plotly (interactive)

```python
import plotly.express as px

fig = px.line(df, x="step", y="loss", color="variant",
              labels={"step": "Training step", "loss": "Loss"})
fig.update_layout(
    template="plotly_white",
    legend_title_text="",
    margin=dict(l=40, r=20, t=40, b=40),
)
fig.write_html("plots/loss.html")        # for sharing
fig.write_image("plots/loss.pdf", scale=2)  # static export (нужен kaleido)
```

## Design principles (Tufte + accessibility)

### 1. Maximize data-ink ratio
Каждый pixel должен нести информацию. Удалить:
- лишние gridlines (или сделать subtle: `ax.grid(alpha=0.3)`)
- top/right spines (`ax.spines.right.set_visible(False)`)
- избыточные axis ticks (`ax.locator_params(nbins=5)`)
- лишние decimal places в labels
- 3D эффекты, drop shadows, gradient fills (chartjunk)

### 2. Colorblind-safe palettes
**По умолчанию используй** `colorblind` или viridis-семейство:
```python
sns.set_palette("colorblind")          # 10 цветов, distinguishable
sns.color_palette("viridis", n)        # для continuous (heatmap)
sns.color_palette("rocket", n)         # ещё одна continuous
```

❌ Не используй: `Set1`, `tab10` без проверки, jet (rainbow — distorts).

Проверка: https://www.color-blindness.com/coblis-color-blindness-simulator/

### 3. Type hierarchy
- Title >= 14pt, axis labels >= 11pt, ticks >= 10pt
- Если делаешь paper — `context="paper"` в seaborn
- Никогда не Comic Sans / decorative fonts

### 4. Choosing the right chart

| Что показать | Тип графика |
|---|---|
| Тренд по времени | line |
| Сравнение категорий | bar (горизонтальный для длинных labels) |
| Распределение | histogram + KDE, violinplot, boxplot |
| Корреляция двух переменных | scatter + regression line |
| Корреляция многих | heatmap (corr matrix), pairplot |
| Композиция (доли) | stacked bar, **не pie** (трудно сравнивать углы) |
| Geographic | choropleth (plotly express) |
| Hierarchical | treemap, sunburst |

❌ Pie-chart почти всегда хуже horizontal bar. ❌ 3D bar/pie всегда хуже 2D. ❌ Dual-y-axes — confuse.

### 5. Annotations > legends
Если возможно — подписать линии прямо на графике вместо legend (легче читать, не нужен взгляд туда-обратно):
```python
ax.text(x_end, y_end, "  Variant A", color=color_a, va="center")
```

### 6. Error bars / uncertainty
**Всегда** показывай неопределённость:
- seaborn делает confidence intervals автоматически (`sns.lineplot` с multiple seeds)
- matplotlib: `ax.errorbar(...)` или `ax.fill_between(x, mean-std, mean+std, alpha=0.2)`

Без uncertainty числа не имеют смысла.

### 7. Размеры для разных контекстов

| Где | Размер | DPI |
|---|---|---|
| NeurIPS/ICML 2-column figure | `(3.5, 2.5)` дюйма | 300 (vector PDF лучше) |
| Beamer slide | `(8, 5)` | 150 |
| Jupyter notebook | `(8, 5)` или default | 100 |
| Twitter | `(8, 4.5)` 16:9 | 150 |

## Workflow для paper figures

```python
# figures/loss_curve.py — один файл = одна figure
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper", palette="colorblind")

df = pd.read_csv("runs/exp_42/metrics.csv")

fig, ax = plt.subplots(figsize=(3.5, 2.5))
sns.lineplot(data=df, x="step", y="loss", hue="variant",
             linewidth=1.5, ax=ax)
ax.set_xlabel("Training step")
ax.set_ylabel("Validation loss")
ax.legend(title="", loc="best", frameon=False, fontsize=8)
ax.grid(alpha=0.3)
sns.despine(ax=ax)

fig.tight_layout()
fig.savefig("paper/figures/loss.pdf", bbox_inches="tight", pad_inches=0.05)
```

`paper/figures/loss.pdf` → `\includegraphics{figures/loss.pdf}` в .tex.

## Multi-panel figures

```python
fig, axes = plt.subplots(1, 2, figsize=(7, 3), sharey=True)

sns.lineplot(data=df, x="step", y="loss", hue="model", ax=axes[0])
axes[0].set_title("(a) Loss")

sns.lineplot(data=df, x="step", y="acc", hue="model", ax=axes[1])
axes[1].set_title("(b) Accuracy")
axes[1].legend().remove()  # одна легенда на оба

fig.tight_layout()
```

Для сложных layout'ов — `gridspec` или `plt.subplot_mosaic("AB;CC")`.

## Common gotchas

| Проблема | Решение |
|---|---|
| Фонт обрезается при save | `bbox_inches="tight"`, `pad_inches=0.05` |
| Утечка памяти в loop | `plt.close(fig)` после save |
| Цвета не consistent между figures | один `set_palette` в начале + `hue_order=[...]` |
| Plotly export to PDF падает | `pip install kaleido` |
| Кириллица не отображается | `plt.rcParams["font.family"] = "DejaVu Sans"` |
| Latex math не рендерится | `plt.rcParams["text.usetex"] = True` (нужен LaTeX установленный) |
| jpg вместо PDF в paper | use `.pdf` extension, matplotlib сам решит формат |

## Hard rules

- **Никогда** не сохранять figures для paper в PNG/JPG — только PDF (vector).
- **Всегда** axis labels с units (`Training step`, не `step`; `Memory (GB)`, не `memory`).
- **Никогда** rainbow/jet colormap — perceptually distorting. Use viridis/plasma.
- **Всегда** colorblind-safe palette — 8% of men have CVD.
- **Никогда** pie chart >5 категорий — bar chart лучше.
- **Всегда** error bars / confidence intervals когда показываешь mean.
- **Никогда** не plot raw data >10k точек без downsampling — figure будет 50MB.
- Перед save: `plt.close(fig)` чтобы не плодить open handles.

## Sources

- Matplotlib vs Seaborn vs Plotly comparison: https://arounddatascience.com/blog/data-visualization/matplotlib-vs-seaborn-vs-plotly-for-eda-dashboards-and-production/
- Best practices Python dataviz: https://medium.com/@abhavya.singh04/data-visualization-best-practices-using-matplotlib-seaborn-and-plotly-eb690043d060
- Top Python dataviz libraries 2026: https://www.carmatec.com/blog/10-best-python-data-visualization-libraries/
- Tufte's principles: see "The Visual Display of Quantitative Information" (Tufte 2001) — chartjunk, data-ink ratio.

## Связанные skills

- **`latex-writing`** — для вставки PDF figures в .tex.
- **`outlines`** (ported) — если нужно структурировать output LLM в табличный формат для plot.
