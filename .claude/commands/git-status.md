Git status + diff stats + recent commits:
!`cd $ALPHA_ROOT && git status -sb 2>/dev/null && echo "── diff ──" && git diff --stat 2>/dev/null && echo "── recent ──" && git log --oneline -5 2>/dev/null || echo "not a git repo"`
