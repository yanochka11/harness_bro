Последние 10 run-директорий в $ALPHA_ROOT/runs/ (size + последняя строка лога):
!`{
  RUNS="$ALPHA_ROOT/runs"
  if [ ! -d "$RUNS" ] || [ -z "$(ls -A $RUNS 2>/dev/null)" ]; then
    echo "no runs yet (mkdir $RUNS at first runner job)"
    exit 0
  fi
  for d in $(ls -1dt $RUNS/*/*/ 2>/dev/null | head -10); do
    size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
    log=$(ls -t "$d"*.log "$d"run.log 2>/dev/null | head -1)
    last=""
    [ -n "$log" ] && last=$(tail -1 "$log" 2>/dev/null | head -c 80)
    printf "%-6s  %s\n         └─ %s\n" "$size" "$d" "$last"
  done
}`
