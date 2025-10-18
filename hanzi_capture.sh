#!/usr/bin/env bash
set -euo pipefail

TMP_DIR="/tmp/hanzi_ocr"
REQ_FILE="$TMP_DIR/request.json"
RES_FILE="$TMP_DIR/response.json"
OUTTXT="$TMP_DIR/hanzi_text.txt"
SERVER_PID="$TMP_DIR/server.pid"
TRAY_SCRIPT="$HOME/.local/bin/hanzi_ocr_tray.py"
IMG="$TMP_DIR/hanzi_screenshot.png"

mkdir -p "$TMP_DIR"

QUIET=false
if [[ "${1:-}" == "--quiet" ]]; then
  QUIET=true
fi

notify_safe() {
  if ! $QUIET; then
    notify-send "$@"
  fi
}

# === inicia o TRAY se não estiver rodando ===
start_tray_if_needed() {
  if pgrep -f "hanzi_ocr_tray.py" >/dev/null 2>&1; then
    return 0
  fi
  notify_safe "🈶 Hanzi OCR" "Iniciando servidor e tray..."
  if command -v setsid >/dev/null 2>&1; then
    setsid env DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
      python3 "$TRAY_SCRIPT" >/dev/null 2>&1 &
  else
    nohup python3 "$TRAY_SCRIPT" >/dev/null 2>&1 &
  fi
  for i in $(seq 1 30); do
    sleep 0.5
    if pgrep -f "python[0-9.]* .*hanzi_ocr_server.py" >/dev/null 2>&1; then
      return 0
    fi
  done
  notify_safe "⚠️ Hanzi OCR" "O servidor não respondeu a tempo."
  exit 1
}

start_tray_if_needed

# === captura imagem ===
rm -f "$IMG"
if command -v spectacle &>/dev/null; then
  spectacle -r -b -o "$IMG"
elif command -v maim &>/dev/null; then
  maim -s "$IMG"
elif command -v gnome-screenshot &>/dev/null; then
  gnome-screenshot -a -f "$IMG"
else
  notify_safe "❌ OCR Chinese (Capture)" "Nenhuma ferramenta de captura encontrada."
  exit 1
fi

# se cancelou
if [ ! -s "$IMG" ]; then
  notify_safe "🈶 OCR Chinese (Capture)" "Captura cancelada."
  exit 0
fi

# === cria requisição e aguarda resposta ===
echo "{\"image\": \"$IMG\"}" > "$REQ_FILE"
REQ_TIME=$(date +%s)

TIMEOUT=20
START=$(date +%s)
while true; do
  if [ -f "$RES_FILE" ]; then
    RES_TIME=$(stat -c %Y "$RES_FILE" 2>/dev/null || echo 0)
    if (( RES_TIME > REQ_TIME )); then
      break
    fi
  fi
  NOW=$(date +%s)
  (( NOW - START > TIMEOUT )) && {
    notify_safe "⏰ Hanzi OCR" "Tempo esgotado aguardando resposta."
    exit 1
  }
  sleep 0.3
done

CHINESE=$(jq -r '.chinese' "$RES_FILE")
PINYIN=$(jq -r '.pinyin' "$RES_FILE")

# pega tradução independente de idioma
TRANSLATION=$(jq -r '.english // .portuguese' "$RES_FILE")

FINAL="Chinese: $CHINESE
Pinyin:  $PINYIN
Translation: $TRANSLATION"

echo "$FINAL" > "$OUTTXT"

# copia pro clipboard
if command -v wl-copy &>/dev/null; then
  echo -n "$FINAL" | wl-copy
elif command -v xclip &>/dev/null; then
  echo -n "$FINAL" | xclip -selection clipboard
fi

notify_safe "🈶 Hanzi OCR" "$FINAL"
echo "$FINAL"
