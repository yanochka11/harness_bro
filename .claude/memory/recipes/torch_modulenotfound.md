---
name: torch-modulenotfound
description: ModuleNotFoundError для torch — обычно нужный CUDA вариант не установлен в активном env
type: recipe
pattern: ModuleNotFoundError.*torch
---

## Problem
`ModuleNotFoundError: No module named 'torch'` при импорте.

## Fix
1. Проверить активный env: `which python` — должен быть `.conda/alpha-env/bin/python`.
2. Если не он: активировать через source `$ALPHA_ROOT/.conda/alpha-env/bin/activate` или `conda activate alpha`.
3. Если env правильный, но torch нет: `pip install torch --index-url https://download.pytorch.org/whl/cu121`.

## Why it works
Часто Jupyter / IDE подхватывает другой python вместо локального alpha-env. CUDA-вариант torch критичен — CPU-only вариант падает на `.cuda()` вызовах.
