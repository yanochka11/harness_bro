Type check Python code:
!`cd $ALPHA_ROOT && (mypy --strict . 2>&1 | tail -40 || pyright . 2>&1 | tail -40 || echo "no type checker")`
