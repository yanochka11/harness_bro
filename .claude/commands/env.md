Окружение (conda, ALPHA_ROOT, HF, W&B, GPU count):
!`{
  echo "── conda ──"; echo "${CONDA_DEFAULT_ENV:-?} | $(python --version 2>&1)"
  echo "── paths ──"
  echo "ALPHA_ROOT=${ALPHA_ROOT:-?}"
  echo "HF_HOME=${HF_HOME:-?}"
  echo "TRANSFORMERS_CACHE=${TRANSFORMERS_CACHE:-?}"
  echo "WANDB_DIR=${WANDB_DIR:-?}"
  echo "── tokens (set/unset) ──"
  for v in HF_TOKEN WANDB_API_KEY GITHUB_TOKEN OPENAI_API_KEY ANTHROPIC_API_KEY; do
    [ -n "${!v}" ] && echo "$v=set(${#!v}…)" || echo "$v=unset"
  done
  echo "── GPUs ──"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>/dev/null | head -8
}`
