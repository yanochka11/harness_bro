#!/usr/bin/env bash
# Claude Code status line. Shows: model | cwd | GPU% | running python procs.
# Skips silently if a tool is missing.
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name // "Claude"' 2>/dev/null || echo "Claude")
cwd=$(echo "$input"   | jq -r '.workspace.current_dir' 2>/dev/null | sed 's|.*/||')

# GPU — only if nvidia-smi present
if command -v nvidia-smi >/dev/null 2>&1; then
    gpu=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    gpu_part="| GPU ${gpu}% "
else
    gpu_part=""
fi

# Running python processes (own user)
procs=$(pgrep -u "$(whoami)" python 2>/dev/null | wc -l | tr -d ' ')

echo "[$model] $cwd $gpu_part| py-procs $procs"
