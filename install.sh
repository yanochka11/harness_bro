#!/usr/bin/env bash
# harness_bro — Claude Code dev environment installer
# https://github.com/yanochka11/harness_bro
#
# Two ways to run:
#
#   1. One-liner (auto-clones repo into a temp dir):
#        curl -fsSL https://raw.githubusercontent.com/yanochka11/harness_bro/main/install.sh | bash
#
#      With flags:
#        curl -fsSL https://.../install.sh | bash -s -- --target /opt/harness --yes
#
#      Override repo / branch:
#        HARNESS_REPO=https://github.com/foo/fork.git HARNESS_BRANCH=dev \
#          bash -c "$(curl -fsSL https://.../install.sh)"
#
#   2. From a local clone:
#        git clone https://github.com/yanochka11/harness_bro.git
#        cd harness_bro && ./install.sh
#
# Flags:
#   --target <path>          where to install (default: $HOME/harness)
#   --tools | --no-tools     install ruff/mypy/pytest via pip
#   --banned-paths <a,b,c>   forbid writes here (HARNESS_BANNED_PATHS env var)
#   --yes | -y               skip all prompts (use defaults)
#
# Idempotent: existing files in target are backed up to <name>.bak on first run.

set -euo pipefail

# ── self-bootstrap (when piped through curl, git-clone the repo) ───
HARNESS_REPO="${HARNESS_REPO:-https://github.com/anthropics/harness_bro.git}"
HARNESS_BRANCH="${HARNESS_BRANCH:-main}"

# Determine: are we running from a real file with .claude/ alongside,
# or were we piped through stdin (cat | bash, curl | bash)?
SELF_FILE="${BASH_SOURCE[0]:-}"
NEED_BOOTSTRAP=1
if [ -n "$SELF_FILE" ] && [ -f "$SELF_FILE" ]; then
    SELF_DIR="$(cd "$(dirname "$(readlink -f "$SELF_FILE")")" && pwd)"
    if [ -d "$SELF_DIR/.claude" ]; then
        NEED_BOOTSTRAP=0
    fi
fi

if [ "$NEED_BOOTSTRAP" -eq 1 ]; then
    # piped via curl|bash or cat|bash — clone the repo and re-exec
    if ! command -v git >/dev/null 2>&1; then
        echo "✗ git not found — cannot self-bootstrap. Install git first." >&2
        exit 1
    fi
    BOOTSTRAP_DIR="$(mktemp -d -t harness_bro.XXXXXX)"
    trap 'rm -rf "$BOOTSTRAP_DIR"' EXIT
    echo "▸ Bootstrapping: cloning $HARNESS_REPO ($HARNESS_BRANCH)..."
    git clone --quiet --depth 1 --branch "$HARNESS_BRANCH" "$HARNESS_REPO" "$BOOTSTRAP_DIR/repo" || {
        echo "✗ git clone failed (HARNESS_REPO=$HARNESS_REPO). Override via:" >&2
        echo "    HARNESS_REPO=https://github.com/your/fork.git bash -c \"\$(curl -fsSL ...)\"" >&2
        exit 1
    }
    echo "✓ cloned to $BOOTSTRAP_DIR/repo"
    exec bash "$BOOTSTRAP_DIR/repo/install.sh" "$@"
fi

# ── colors / pretty ───────────────────────────────────────────────
if [ -t 1 ]; then
    BOLD=$'\033[1m'; DIM=$'\033[2m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; B=$'\033[34m'; N=$'\033[0m'
else
    BOLD=""; DIM=""; G=""; Y=""; R=""; B=""; N=""
fi

say()  { printf "%s\n" "$*"; }
info() { printf "${B}▸${N} %s\n" "$*"; }
ok()   { printf "${G}✓${N} %s\n" "$*"; }
warn() { printf "${Y}⚠${N} %s\n" "$*"; }
err()  { printf "${R}✗${N} %s\n" "$*" >&2; }

# ── banner ────────────────────────────────────────────────────────
cat <<BANNER
${BOLD}
  ┌──────────────────────────────────────────────────────────────┐
  │   harness_bro — Claude Code dev environment installer        │
  │   Hooks · Skills · Subagents · Memory · Auto-fix loop        │
  └──────────────────────────────────────────────────────────────┘
${N}
BANNER

# ── parse args ────────────────────────────────────────────────────
TARGET=""
INSTALL_TOOLS=""
BANNED_PATHS=""
NON_INTERACTIVE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)         TARGET="$2"; NON_INTERACTIVE=1; shift 2 ;;
        --no-tools)       INSTALL_TOOLS="n"; NON_INTERACTIVE=1; shift ;;
        --tools)          INSTALL_TOOLS="y"; NON_INTERACTIVE=1; shift ;;
        --banned-paths)   BANNED_PATHS="$2"; NON_INTERACTIVE=1; shift 2 ;;
        --yes|-y)         NON_INTERACTIVE=1; shift ;;
        -h|--help)        sed -n '2,18p' "$0"; exit 0 ;;
        *) err "Unknown arg: $1"; exit 1 ;;
    esac
done

# ── proxy detection (для MLSpace и закрытых сетей) ────────────────
if [ -n "${HTTPS_PROXY:-${https_proxy:-}}" ] || [ -n "${HTTP_PROXY:-${http_proxy:-}}" ]; then
    PROXY_URL="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"
    # маскируем credentials в выводе
    PROXY_DISPLAY=$(echo "$PROXY_URL" | sed -E 's|://[^@]+@|://***:***@|')
    ok "proxy: $PROXY_DISPLAY"
    # подсказываем npm/pip использовать proxy явно (на всякий случай)
    if command -v npm >/dev/null 2>&1; then
        npm config set proxy "$PROXY_URL" >/dev/null 2>&1 || true
        npm config set https-proxy "$PROXY_URL" >/dev/null 2>&1 || true
    fi
fi

# ── prereqs ───────────────────────────────────────────────────────
info "Checking prerequisites..."
missing=()
for tool in python3 node npm git; do
    if command -v "$tool" >/dev/null 2>&1; then
        ok "$tool — $(command -v "$tool")"
    else
        err "$tool — not found"
        missing+=("$tool")
    fi
done

# Python ≥3.10
if command -v python3 >/dev/null; then
    PYV=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
    if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
        ok "python $PYV (>= 3.10)"
    else
        err "python $PYV — need >= 3.10"
        missing+=("python>=3.10")
    fi
fi

if [ ${#missing[@]} -gt 0 ]; then
    err "Missing: ${missing[*]}"
    say "  Install on Debian/Ubuntu: sudo apt install python3 nodejs npm git"
    say "  Install on macOS:          brew install python node git"
    exit 1
fi

# Claude Code CLI
if command -v claude >/dev/null 2>&1; then
    ok "claude (Claude Code) — $(claude --version 2>/dev/null | head -1 || echo present)"
else
    warn "claude CLI not found"
    say "    install: ${BOLD}npm install -g @anthropic-ai/claude-code${N}"
    say "    or visit: https://claude.ai/code"
fi

# Connectivity test (важно для MLSpace / proxy-окружений)
info "Testing network connectivity..."
if curl -fsSL --max-time 10 https://github.com -o /dev/null 2>/dev/null; then
    ok "github.com reachable"
else
    warn "github.com unreachable — нужен proxy?"
    say "    For MLSpace / corporate networks:"
    say "      ${BOLD}export HTTPS_PROXY=http://USER:PASS@HOST:PORT${N}"
    say "      ${BOLD}export HTTP_PROXY=http://USER:PASS@HOST:PORT${N}"
    say "      ${BOLD}export NO_PROXY=localhost,127.0.0.1${N}"
    say "    Затем перезапустите install.sh"
fi
echo

# ── target dir ────────────────────────────────────────────────────
DEFAULT_TARGET="$HOME/harness"
if [ -z "$TARGET" ]; then
    if [ -t 0 ] && [ "$NON_INTERACTIVE" -eq 0 ]; then
        # stdin is a TTY — ask
        read -rp "Install to [${DEFAULT_TARGET}]: " input
        TARGET="${input:-$DEFAULT_TARGET}"
    else
        # piped / non-interactive — silent default
        TARGET="$DEFAULT_TARGET"
        info "Non-interactive mode — using default target $TARGET"
    fi
fi
mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
ok "Target: $TARGET"

SRC="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")" && pwd)"
if [ ! -d "$SRC/.claude" ]; then
    err "$SRC/.claude not found — run install.sh from the harness_bro repo root"
    exit 1
fi

# ── copy config ───────────────────────────────────────────────────
info "Copying Claude Code config..."

backup() {
    local p="$1"
    if [ -e "$p" ] && [ ! -e "$p.bak" ]; then
        cp -r "$p" "$p.bak"
        ok "  backed up $(basename "$p") → $(basename "$p").bak"
    fi
    return 0
}

backup "$TARGET/.claude"
backup "$TARGET/CLAUDE.md"
backup "$TARGET/.mcp.json"
backup "$TARGET/.gitignore"

# Copy .claude/ (excluding state/sessions/cache)
mkdir -p "$TARGET/.claude"
for d in agents commands hooks skills memory; do
    if [ -d "$SRC/.claude/$d" ]; then
        cp -r "$SRC/.claude/$d" "$TARGET/.claude/"
    fi
done
cp "$SRC/.claude/settings.json" "$TARGET/.claude/settings.json"
ok "  .claude/{agents,commands,hooks,skills,memory,settings.json}"

cp "$SRC/.gitignore" "$TARGET/.gitignore"
ok "  .gitignore"

if [ -f "$SRC/README.md" ]; then
    cp "$SRC/README.md" "$TARGET/README.md"
    ok "  README.md"
fi
if [ -f "$SRC/LICENSE" ]; then
    cp "$SRC/LICENSE" "$TARGET/LICENSE"
fi

# ── render CLAUDE.md from template ────────────────────────────────
info "Rendering CLAUDE.md..."
if [ -n "$BANNED_PATHS" ]; then
    BANNED_RULE="**Banned writes**: \`${BANNED_PATHS//,/\`, \`}\` (see HARNESS_BANNED_PATHS env var)"
else
    BANNED_RULE="No banned write-paths (set HARNESS_BANNED_PATHS env var to enable nfs_guard)"
fi
sed -e "s|@@WORKSPACE@@|$TARGET|g" \
    -e "s|@@BANNED_RULE@@|$BANNED_RULE|g" \
    "$SRC/CLAUDE.md.template" > "$TARGET/CLAUDE.md"
ok "  CLAUDE.md"

# ── render .mcp.json ──────────────────────────────────────────────
info "Rendering .mcp.json..."
sed "s|@@WORKSPACE@@|$TARGET|g" "$SRC/.mcp.json.template" > "$TARGET/.mcp.json"
ok "  .mcp.json (filesystem MCP scoped to $TARGET)"

# ── chmod +x hooks ────────────────────────────────────────────────
info "Making hooks executable..."
chmod +x "$TARGET"/.claude/hooks/*.py "$TARGET"/.claude/hooks/*.sh 2>/dev/null || true
ok "  done"

# ── settings.json: deny + env ─────────────────────────────────────
if [ -n "$BANNED_PATHS" ]; then
    info "Adding banned paths to settings.json deny list..."
    python3 - "$TARGET/.claude/settings.json" "$BANNED_PATHS" <<'PYEOF'
import json, sys
path, banned = sys.argv[1], sys.argv[2]
d = json.load(open(path))
d.setdefault("permissions", {}).setdefault("deny", [])
for p in banned.split(","):
    p = p.strip().rstrip("/")
    if not p:
        continue
    for entry in (f"Write({p}/**)", f"Edit({p}/**)"):
        if entry not in d["permissions"]["deny"]:
            d["permissions"]["deny"].append(entry)
json.dump(d, open(path, "w"), indent=2)
PYEOF
    ok "  added"
fi

# ── install Python tools ──────────────────────────────────────────
if [ -z "$INSTALL_TOOLS" ]; then
    if [ -t 0 ] && [ "$NON_INTERACTIVE" -eq 0 ]; then
        read -rp "Install ruff + mypy + pytest via pip? [y/N]: " yn
        INSTALL_TOOLS="${yn:-n}"
    else
        INSTALL_TOOLS="n"
    fi
fi
if [[ "$INSTALL_TOOLS" =~ ^[Yy] ]]; then
    info "Installing Python dev tools..."
    pip install --quiet --upgrade ruff mypy pytest pyright || warn "pip install failed (you can do it later)"
    ok "  ruff / mypy / pytest / pyright"
fi

# ── done ──────────────────────────────────────────────────────────
cat <<EOF

${G}${BOLD}✓ harness_bro installed to:${N} $TARGET

${BOLD}Next steps:${N}

  ${DIM}# 1. enter the workspace${N}
  cd $TARGET

  ${DIM}# 2. (optional) export env vars${N}
  export HF_HOME=\$PWD/.cache/huggingface       # or your shared cache
  export HARNESS_BANNED_PATHS=                  # comma-sep, e.g. /home/foo
  export GITHUB_TOKEN=ghp_...                   # for github MCP server

  ${DIM}# 3. start Claude Code${N}
  claude

${BOLD}Quick reference once in Claude:${N}

  ${G}/env${N} ${G}/gpu${N} ${G}/pytest${N} ${G}/lint${N}        # slash commands (read-only snapshots)
  «${Y}напиши${N}» «${Y}падает${N}» «${Y}запусти${N}»          # триггерят subagents
  «${Y}запомни этот фикс${N}»                # добавить recipe в memory
  «${Y}оптимизируй setup${N}»                # self-improve audit

${BOLD}Docs:${N}
  $TARGET/README.md           # full guide
  $TARGET/CLAUDE.md           # what Claude reads at session start
  $TARGET/.claude/skills/     # 90+ skills available

Happy coding!
EOF
