Run all available linters in current project:
!`cd $ALPHA_ROOT && {
  command -v ruff &>/dev/null && echo "── ruff ──" && ruff check . 2>&1 | tail -30
  command -v mypy &>/dev/null && echo "── mypy ──" && mypy . 2>&1 | tail -20
  command -v black &>/dev/null && echo "── black ──" && black --check . 2>&1 | tail -10
} || echo "no linters installed"`
