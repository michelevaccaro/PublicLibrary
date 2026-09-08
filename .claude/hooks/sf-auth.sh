#!/bin/bash
set -euo pipefail

# Only runs in Claude Code remote (web) sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

KEY_FILE_B64="$CLAUDE_PROJECT_DIR/.claude/hooks/sf-jwt-key.b64"
if [ ! -f "$KEY_FILE_B64" ]; then
  exit 0
fi

if ! command -v sf >/dev/null 2>&1; then
  npm install -g @salesforce/cli >/dev/null 2>&1
fi

KEY_DIR="$HOME/.sf-jwt"
mkdir -p "$KEY_DIR"
base64 -d "$KEY_FILE_B64" > "$KEY_DIR/server.key"
chmod 600 "$KEY_DIR/server.key"

sf org login jwt \
  --client-id "3MVG97L7PWbPq6UwCxIwswvrWkTR8RwnmC7KywxWwSGmilCdEVxerHrQ.ut__cbqXgw6R5dFT6SqW7NYWuNxw" \
  --jwt-key-file "$KEY_DIR/server.key" \
  --username "michele.vaccaro+1.34b7b8355677@agentforce.com" \
  --instance-url "https://orgfarm-19715883a0-dev-ed.develop.my.salesforce.com" \
  --alias b2b \
  --set-default \
  --json >/dev/null 2>&1 || true
