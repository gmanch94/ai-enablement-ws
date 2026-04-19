#!/bin/bash
INPUT=$(cat)
FILE=$(python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('file_path', '') or ti.get('path', ''))
" <<< "$INPUT" 2>/dev/null)

if [[ "$FILE" == *"decisions/"* ]]; then
  echo "[HOOK] ADR saved → update README.md ADR list; verify CLAUDE.md conventions still current"
elif [[ "$FILE" == *"reference/"* ]]; then
  echo "[HOOK] Cheatsheet updated → review existing ADRs for this cloud for potential amendments"
elif [[ "$FILE" == *"projects/"* ]]; then
  echo "[HOOK] Project file updated → does this reflect an architectural decision? Consider /adr"
fi
