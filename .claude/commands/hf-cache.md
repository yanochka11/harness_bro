HuggingFace cache: total + top-10 models + top-5 datasets:
!`{
  CACHE="${HF_HOME:-$HOME/.cache/huggingface}"
  if [ ! -d "$CACHE" ]; then
    echo "no cache dir at $CACHE (set HF_HOME or run anything that downloads from HF)"
    exit 0
  fi
  echo "── total ──"
  du -sh "$CACHE" 2>/dev/null
  echo ""
  echo "── top-10 biggest models ──"
  du -sh "$CACHE/hub"/models--* 2>/dev/null | sort -hr | head -10
  echo ""
  echo "── top-5 datasets ──"
  du -sh "$CACHE/hub"/datasets--* 2>/dev/null | sort -hr | head -5
}`
