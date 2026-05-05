Запущенные python/training/eval процессы (мои + GPU compute apps):
!`{
  echo "── мои python (top 15 по %CPU) ──"
  ps -u $(whoami) -o pid,pcpu,pmem,etime,cmd --sort=-pcpu | grep -E '(python|train|eval|run\.py|jupyter|wandb)' | grep -v grep | head -15
  echo ""
  echo "── GPU compute-apps ──"
  nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory,process_name --format=csv,noheader 2>/dev/null | head -10
  echo ""
  echo "── tmux ──"
  tmux ls 2>/dev/null || echo "no tmux sessions"
}`
