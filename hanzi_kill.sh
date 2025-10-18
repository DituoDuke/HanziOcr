#!/usr/bin/env bash
set -euo pipefail

# Diretório base (mantém consistência com os outros scripts)
BASE_DIR="$(dirname "$0")"

TMP_DIR="/tmp/hanzi_ocr"
PID_FILE="$TMP_DIR/server.pid"

# === encerra servidor se PID válido ===
if [ -f "$PID_FILE" ]; then
  pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
  if [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1; then
    kill "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    notify-send "🔴 Hanzi OCR" "Servidor encerrado (PID $pid)."
  fi
fi

# === encerra qualquer servidor Python órfão ===
pkill -f "hanzi_ocr_server.py" 2>/dev/null || true

# === encerra o tray ===
pkill -f "hanzi_ocr_tray.py" 2>/dev/null || true

# === limpa arquivos temporários ===
rm -f "$TMP_DIR"/*.json "$TMP_DIR"/*.png "$TMP_DIR"/*.mp3 2>/dev/null || true

notify-send "🧹 Hanzi OCR" "Todos os processos e temporários foram encerrados."
