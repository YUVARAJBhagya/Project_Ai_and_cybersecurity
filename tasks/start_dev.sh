#!/bin/bash

if [[ -f ".env.dev" && -s ".env.dev" ]]; then
  if grep -qE '^[a-zA-Z_][a-zA-Z0-9_]*=.*' .env.dev; then
    export $(grep -v '^#' .env.dev | xargs)
  else
    echo "Malformed lines in .env.dev"
    exit 1
  fi
else
  echo ".env.dev is missing or empty"
fi

uv run uvicorn a4s_eval.main:app --host 0.0.0.0 --port 8001 --reload
