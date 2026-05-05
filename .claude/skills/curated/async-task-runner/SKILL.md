---
name: async-task-runner
description: Use to launch, monitor, and manage long-running background tasks — training, evaluation, batch processing. Provides nohup + log + PID file pattern, tmux integration, monitoring helpers. Triggers запусти в фоне, run in background, мониторь, что там, kill процесс.
allowed-tools: [Bash, Read]
model: sonnet
---

# Async Task Runner

## Standard launch pattern
```bash
TASK_NAME=<short-name>
RUN_DIR=$ALPHA_ROOT/runs/$TASK_NAME/$(date +%Y-%m-%d_%H-%M-%S)
mkdir -p $RUN_DIR

nohup <command> > $RUN_DIR/run.log 2>&1 &
PID=$!
echo $PID > $RUN_DIR/pid

echo "started pid=$PID log=$RUN_DIR/run.log"
```

## tmux variant (for runs needing interactive attach)
```bash
tmux new-session -d -s $TASK_NAME "cd $PROJECT && <command> 2>&1 | tee $RUN_DIR/run.log"
```

## Monitor
```bash
# all bg jobs
jobs -l

# my python procs
ps -u $USER -o pid,etime,pcpu,pmem,cmd | grep -E 'python|accelerate|torchrun' | grep -v grep

# tail latest run log
tail -F $(ls -t $ALPHA_ROOT/runs/*/*/run.log | head -1)

# disk usage
du -sh $ALPHA_ROOT/runs/*/* | sort -h | tail -20
```

## Stop
```bash
kill -TERM <PID>            # graceful (allows cleanup)
pkill -TERM -f '<pattern>'  # graceful for all matching
kill -KILL <PID>            # only if graceful didn't work in 30s
```

## Hard rules
- ALWAYS save log to file — never just `&` with no redirect
- ALWAYS write pid to RUN_DIR/pid
- NEVER use SIGKILL (-9) first — corrupts state
- NEVER run training/eval in foreground (blocks chat)
- All RUN_DIR under $ALPHA_ROOT/runs/, never /tmp/
