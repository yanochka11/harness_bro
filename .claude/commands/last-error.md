Last 50 lines containing 'error' or 'traceback' from runs/:
!`grep -riE 'error|traceback|exception' $ALPHA_ROOT/runs/ 2>/dev/null | tail -50 || echo "no run logs yet"`
