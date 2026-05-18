#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/ecom"
VENV="$SKILL_DIR/.venv"

echo "Installing Claude ECOM..."

mkdir -p "$SKILL_DIR"
cp -r . "$SKILL_DIR/"

python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r requirements.txt

# Register skills
SKILLS_TARGET="$HOME/.claude/skills"
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$SKILL_DIR/skills/$name" "$SKILLS_TARGET/$name" 2>/dev/null || true
done

echo "Claude ECOM installed. Use /ecom audit <url> to start."
