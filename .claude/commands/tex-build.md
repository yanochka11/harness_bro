Build LaTeX document via latexmk (auto-detects bib + reruns):
!`{
  if ! command -v latexmk >/dev/null 2>&1; then
    echo "latexmk не найден. Установи TeX Live: apt install texlive-full / brew install --cask mactex"
    exit 0
  fi
  MAIN=$(ls main.tex paper.tex *.tex 2>/dev/null | head -1)
  if [ -z "$MAIN" ]; then
    echo "не нашёл .tex файл в текущей директории"
    exit 0
  fi
  echo "── building $MAIN ──"
  latexmk -pdf -interaction=nonstopmode -file-line-error "$MAIN" 2>&1 | tail -30
  echo ""
  echo "── PDF size ──"
  ls -lh "${MAIN%.tex}.pdf" 2>/dev/null
}`
