#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.streamlit.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "cmyLLMz zaten kapalı."
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    rm -f "$PID_FILE"
    echo "✓ cmyLLMz durduruldu."
else
    rm -f "$PID_FILE"
    echo "cmyLLMz zaten kapalıydı."
fi
