#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/ecom"
VENV="$SKILL_DIR/.venv"

echo "Installing Claude ECOM..."

# -- Python version check -----------------------------------------------------
# Claude ECOM relies on type-hint syntax introduced in Python 3.10
# (e.g. `str | None` at runtime in some helpers). Fail fast with a clear
# message rather than blowing up partway through `pip install`.
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not on PATH. Install Python 3.10+ and re-run." >&2
  exit 1
fi

PY_VER="$(python3 -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')"
PY_OK="$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 10) else 0)')"
if [ "$PY_OK" != "1" ]; then
  echo "Error: Claude ECOM requires Python 3.10 or newer. Found Python ${PY_VER}." >&2
  echo "Install a newer Python (https://www.python.org/downloads/) and re-run." >&2
  exit 1
fi

# -- Copy repo into the skill dir, excluding noisy paths ----------------------
# rsync is preferred over `cp -r .` because the latter copies .git, caches,
# editor cruft, and any vendor directories that happen to be present.
mkdir -p "$SKILL_DIR"
if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is required but not found on PATH." >&2
  echo "macOS: rsync ships with the OS. Linux: install via apt/dnf/pacman." >&2
  exit 1
fi

rsync -a \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='.DS_Store' \
  ./ "$SKILL_DIR/"

# -- Bootstrap the virtualenv -------------------------------------------------
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r requirements.txt

# -- Register skills ----------------------------------------------------------
SKILLS_TARGET="$HOME/.claude/skills"
mkdir -p "$SKILLS_TARGET"
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$SKILL_DIR/skills/$name" "$SKILLS_TARGET/$name" 2>/dev/null || true
done

echo "Claude ECOM installed. Use /ecom audit <url> to start."
