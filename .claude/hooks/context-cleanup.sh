#!/bin/bash
CONTEXT="/c/Users/giris/Documents/GitHub/ai-enablement-ws/context"
FILES=$(find "$CONTEXT" -name "*.md" ! -name ".gitkeep" 2>/dev/null)
if [ -n "$FILES" ]; then
  echo "[HOOK] Active context files — review for staleness:"
  echo "$FILES"
fi
