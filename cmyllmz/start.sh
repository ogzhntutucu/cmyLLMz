#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.streamlit.pid"
STREAMLIT="$SCRIPT_DIR/venv/bin/streamlit"
APP="$SCRIPT_DIR/src/app.py"
PORT=8501

# Zaten çalışıyorsa uyar
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "cmyLLMz zaten çalışıyor (PID $OLD_PID)"
        echo "→ http://localhost:$PORT"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

cd "$SCRIPT_DIR"
echo "cmyLLMz başlatılıyor..."
"$STREAMLIT" run "$APP" \
    --server.port "$PORT" \
    --server.headless true \
    --browser.gatherUsageStats false \
    > "$SCRIPT_DIR/.streamlit.log" 2>&1 &

echo $! > "$PID_FILE"
sleep 2

echo "✓ cmyLLMz hazır → http://localhost:$PORT"
echo "  Durdurmak için: ./stop.sh"

xdg-open "http://localhost:$PORT" 2>/dev/null || true
