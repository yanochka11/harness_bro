HF cache size (uses $HF_HOME, default ~/.cache/huggingface):
!`du -sh "${HF_HOME:-$HOME/.cache/huggingface}" 2>/dev/null || echo "(не установлен)"`
