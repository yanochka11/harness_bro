Auto-format Python code:
!`cd $ALPHA_ROOT && {
  command -v ruff &>/dev/null && ruff format . && echo "✓ ruff format"
  command -v black &>/dev/null && black --quiet . && echo "✓ black"
  command -v isort &>/dev/null && isort --quiet . && echo "✓ isort"
}`
