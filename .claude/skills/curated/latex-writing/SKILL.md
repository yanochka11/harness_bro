---
name: latex-writing
description: Use when writing or editing LaTeX (.tex) documents — articles, reports, theses, preprints, conference papers; or working with Overleaf projects via git. Triggers latex, .tex, overleaf, статья в латех, отчёт latex, paper, preprint, технический отчёт, диссертация, beamer, biblatex, bibliography. Knows project structure, packages, math/figures/tables/bib, common errors, latexmk build.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, WebFetch]
model: sonnet
---

# LaTeX Writing — статьи, отчёты, диссертации, Overleaf

## Когда

- «напиши статью в latex», «.tex», «overleaf», «технический отчёт», «препринт», «диссертация», «beamer слайды»
- Правка существующих `.tex` файлов
- Подготовка bibliography (`.bib`)
- Сборка локально (`latexmk`/`pdflatex`) или через Overleaf

## Прежде чем писать

1. **Уточнить целевой формат**: статья (`article`), технический отчёт (`report`), книга (`book`), презентация (`beamer`), letter (`letter`).
2. **Уточнить целевой venue**: NeurIPS/ICML/ICLR (есть готовые class-файлы), arXiv, Overleaf-template, IEEE, ACM, Springer, кастомный.
3. Если есть существующий `.tex` — `Read` его + `\documentclass{...}` строку, чтобы понять class и стиль.
4. Если venue даёт template — скачать его (`*.cls` + main.tex), не изобретать своё.

## Структура проекта (рекомендуемая)

```
paper/
├── main.tex              ← главный файл со \documentclass и \begin{document}
├── preamble.tex          ← \usepackage{...}, \newcommand, метаданные
├── sections/
│   ├── 01-intro.tex
│   ├── 02-related.tex
│   ├── 03-method.tex
│   ├── 04-experiments.tex
│   ├── 05-discussion.tex
│   └── 06-conclusion.tex
├── figures/              ← .pdf / .png / .tikz
├── tables/               ← .tex включаемые через \input
├── refs.bib              ← biblatex/bibtex bibliography
├── latexmkrc             ← конфиг для latexmk
└── .gitignore            ← *.aux *.log *.out *.bbl *.blg *.toc *.synctex.gz
```

`main.tex` сшивает разделы через `\input{sections/01-intro}`. Это даёт чистые diff'ы и параллельную работу нескольких авторов.

## Минимальный шаблон для статьи (article)

```latex
\documentclass[11pt,a4paper]{article}

% — базовые packages —
\usepackage[utf8]{inputenc}        % для русского/UTF-8 если нужно
\usepackage[T1]{fontenc}
\usepackage[english,russian]{babel} % multilingual
\usepackage{geometry}              % \geometry{margin=2.5cm}
\usepackage{microtype}             % качественный набор

% — math —
\usepackage{amsmath, amssymb, amsthm, mathtools}

% — figures, tables, layout —
\usepackage{graphicx}
\usepackage{booktabs}              % \toprule \midrule \bottomrule
\usepackage{caption, subcaption}
\usepackage{float}

% — links и references —
\usepackage[hidelinks]{hyperref}   % clickable links
\usepackage{cleveref}              % \cref{...} вместо ручного "Figure"

% — bibliography —
\usepackage[backend=biber,style=alphabetic,sorting=ynt]{biblatex}
\addbibresource{refs.bib}

% — числа и единицы —
\usepackage{siunitx}

\title{Your Paper Title}
\author{Author One \and Author Two}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
One paragraph: problem, method, key result, contribution.
\end{abstract}

\input{sections/01-intro}
\input{sections/02-related}
\input{sections/03-method}
\input{sections/04-experiments}
\input{sections/05-conclusion}

\printbibliography
\end{document}
```

## Минимальный шаблон для технического отчёта (report)

```latex
\documentclass[11pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english,russian]{babel}
\usepackage{geometry}
\usepackage{graphicx, booktabs, hyperref, cleveref}
\usepackage[backend=biber]{biblatex}
\addbibresource{refs.bib}

\title{Project Report: Topic}
\author{Author Name}
\date{\today}

\begin{document}
\maketitle
\tableofcontents

\chapter{Introduction}
\input{ch01}

\chapter{Methodology}
\input{ch02}

\chapter{Results}
\input{ch03}

\chapter{Discussion}
\input{ch04}

\printbibliography
\end{document}
```

`\chapter` доступен в `report`/`book`, но не в `article`.

## Главные конструкции

### Math

```latex
\begin{equation}
    \mathcal{L}(\theta) = \mathbb{E}_{x \sim \mathcal{D}}[\ell(f_\theta(x), y)]
\label{eq:loss}
\end{equation}

% Inline: $E = mc^2$
% Numbered system: \begin{align} a &= b \\ c &= d \end{align}
% Unnumbered: \begin{align*} ... \end{align*}
```

Используй `\cref{eq:loss}` (с пакетом `cleveref`) — оно само напишет «equation 3», «Figure 5», «Section 2».

### Figures

```latex
\begin{figure}[t]
    \centering
    \includegraphics[width=0.8\linewidth]{figures/loss_curve.pdf}
    \caption{Training loss over epochs.}
    \label{fig:loss}
\end{figure}
```

PDF figures > PNG > JPG (для научных). TikZ — для диаграмм генерируемых из текста. Подпись **под** фигурой (caption после includegraphics).

### Tables

`booktabs` обязателен — даёт правильные горизонтальные линии:

```latex
\begin{table}[t]
    \centering
    \caption{Results on benchmark X.}
    \label{tab:results}
    \begin{tabular}{lrr}
        \toprule
        Method & Accuracy & F1 \\
        \midrule
        Baseline & 0.823 & 0.811 \\
        Ours     & \textbf{0.876} & \textbf{0.864} \\
        \bottomrule
    \end{tabular}
\end{table}
```

### Bibliography (biblatex + biber)

`refs.bib`:
```bibtex
@article{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and others},
  journal={NeurIPS},
  year={2017}
}
```

В тексте: `\cite{vaswani2017attention}` или `\cite[p.~5]{vaswani2017attention}`.

### Числа и единицы

`siunitx` — стандарт-де-факто:
```latex
The model trained for \qty{72}{\hour} on \qty{8}{\gibi\byte} GPUs,
processing \num{12345} samples.
```

Не пиши `72 hours` руками — `\qty{72}{\hour}` гарантирует non-breaking spaces и единый стиль.

## Best practices (адаптировано из dspinellis/latex-advice)

1. **Одна фраза — одна строка**. Перенос строки после каждой phrase или logical unit, **не** на 80-й колонке. Diff'ы становятся читаемыми.
2. **Custom commands для terminology**:
   ```latex
   \newcommand{\ours}{\textsc{HarnessBro}\xspace}
   \newcommand{\dataset}{ImageNet-1k\xspace}
   ```
   Меняешь раз — работает везде.
3. **Не использовать `\\`** в тексте для разрыва строки (только в таблицах). Используй `\par` или абзацный перенос.
4. **Версионируй .bib файл**, но _не_ `*.aux`, `*.log`, `*.bbl`, `*.synctex.gz` (см. .gitignore).
5. **Никогда не пиши `\\textit`/`\\textbf` для семантики** — определи `\emph{}` или свой `\finding{}`.

## Build (локально)

```bash
# latexmk — самый правильный способ. Сам разберётся когда нужен biber/bibtex.
latexmk -pdf -interaction=nonstopmode -file-line-error main.tex

# Очистить временные файлы
latexmk -c

# Полная очистка
latexmk -C

# Вотч-режим (пересобирает при изменениях)
latexmk -pdf -pvc main.tex
```

Альтернатива: `pdflatex main && biber main && pdflatex main && pdflatex main`.

`latexmkrc` для проекта:
```perl
$pdf_mode = 1;
$bibtex_use = 2;
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O %S';
```

## Overleaf

### Git integration (clone проект локально)

```bash
# 1. На Overleaf: Menu → Sync → Git → копируешь URL
# 2. Локально:
git clone https://git.overleaf.com/PROJECT_ID
cd PROJECT_ID
# теперь обычный git workflow
```

Token: Account Settings → Git Authentication Token (не пароль).

### Push изменения обратно

```bash
# Стандартный поток
git add .
git commit -m "fix typos in section 3"
git push

# Если проект уже на GitHub и хочешь зеркалить в Overleaf:
git remote add overleaf https://git.overleaf.com/PROJECT_ID
git push overleaf master --set-upstream
```

### Pull изменения с Overleaf (если соавторы редактируют там)

```bash
git pull overleaf master --rebase=false
# первый pull может потребовать --allow-unrelated-histories
```

### Common Overleaf compile errors

| Ошибка | Что делать |
|---|---|
| `Undefined control sequence \something` | Не подключён нужный package. Добавь `\usepackage{...}` в preamble. |
| `File 'foo.sty' not found` | Package не установлен в TeX Live на Overleaf. Скорее всего опечатка в имени, или нужен другой compiler. Menu → Settings → TeX Live version. |
| `Bibliography compile failed` | Menu → Settings → Compiler → BibTeX → биber или наоборот. Также проверь синтаксис `.bib`. |
| `Latex error: file ended while scanning` | Незакрытая `\begin{...}`/`{...}`. Найти grep'ом. |
| Figures not showing | `\graphicspath{{figures/}}` в preamble + правильный путь в `\includegraphics{}`. |
| `! Package inputenc Error` | На Overleaf переключи compiler с `pdfLaTeX` на `XeLaTeX` или `LuaLaTeX` для UTF-8/кириллицы. |

### Кириллица на Overleaf

Если статья на русском — лучше **XeLaTeX**:
```latex
\documentclass[11pt]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setotherlanguage{english}
\setmainfont{CMU Serif}  % или Times New Roman, Liberation Serif
```
Compile: Menu → Settings → Compiler → **XeLaTeX**.

## Workflow (когда писать с нуля)

1. **Структура** — создай файлы по skeleton (main.tex + sections/ + refs.bib).
2. **Outline** — заполни заголовки секций перед текстом. Покажи пользователю outline → approve.
3. **По одной секции** — пиши, проверяй компиляцию `latexmk -pdf main.tex`.
4. **Bibliography по ходу** — добавляй `@article{...}` в refs.bib когда цитируешь, не оставляй на конец.
5. **Figures** — отдельная директория `figures/`, всегда `.label{fig:...}` для cross-ref через `\cref`.
6. **Финальная проверка** — `latexmk -c` (cleanup), потом `latexmk -pdf` снова — должна быть warning-free сборка.

## Hard rules

- Никогда не закоммитить `*.aux`, `*.log`, `*.bbl`, `*.synctex.gz` — добавь в `.gitignore`.
- Никогда `~` не использовать для пробела внутри текста (используй `\,` или non-breaking `~` правильно: `Section~3`).
- Не вставлять PNG скриншоты графиков — генерируй PDF (matplotlib `plt.savefig('fig.pdf')`).
- Bibliography keys — стабильные (`vaswani2017attention`), не `[1]`, `[2]`.
- Перед `git push` на Overleaf — собирать локально, чтобы не плодить commits с broken builds.

## References

- LaTeX2e core docs: https://latex-project.org/help/documentation/
- Overleaf docs: https://www.overleaf.com/learn
- LaTeX best practices: https://github.com/dspinellis/latex-advice
- biblatex manual: https://ctan.org/pkg/biblatex
- siunitx: https://ctan.org/pkg/siunitx

Если нужны актуальные docs по конкретному пакету — `WebFetch` → ctan.org/pkg/<package>, или используй context7 MCP с library `/latex3/latex2e`.
