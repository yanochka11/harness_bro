Последние 10 W&B runs (по локальной директории + summary if installed):
!`{
  WB_DIR="${WANDB_DIR:-$ALPHA_ROOT/wandb}"
  if [ -d "$WB_DIR" ]; then
    echo "── local ($WB_DIR) ──"
    ls -lt "$WB_DIR"/run-* 2>/dev/null | head -10
  else
    echo "no local wandb dir at $WB_DIR"
  fi
  echo ""
  echo "── runs/ logs ──"
  ls -lt "$ALPHA_ROOT/runs"/*/*/run.log 2>/dev/null | head -5
  echo ""
  if command -v wandb >/dev/null; then
    echo "── wandb status ──"
    wandb status 2>&1 | head -10
  fi
}`
