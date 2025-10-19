#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(dirname "$0")"

TMP_DIR="/tmp/hanzi_ocr"
mkdir -p "$TMP_DIR"
RES_FILE="$TMP_DIR/response.json"
TMP_MP3="$TMP_DIR/hanzi_tts.mp3"

if [ -x "$BASE_DIR/hanzi_capture.sh" ]; then
  "$BASE_DIR/hanzi_capture.sh" --quiet >/dev/null || {
    notify-send "🛑 Cancelado" "Captura cancelada ou falhou."
    exit 0
  }
else
  notify-send "Erro" "hanzi_capture.sh não encontrado em $BASE_DIR/"
  exit 1
fi

if [ ! -s "$RES_FILE" ]; then
  notify-send "🛑 Cancelado" "Nenhum resultado OCR encontrado."
  exit 0
fi

CHINESE=$(jq -r '.chinese' "$RES_FILE")
PINYIN=$(jq -r '.pinyin' "$RES_FILE")
TRANSLATION=$(jq -r '.english // .portuguese' "$RES_FILE")

if [ -z "$CHINESE" ] || [ "$CHINESE" = "(nenhum texto detectado)" ]; then
  notify-send "🈶 OCR Chinese" "Nenhum texto detectado."
  exit 0
fi

FINAL="Chinese: $CHINESE
Pinyin: $PINYIN
Translation: $TRANSLATION"

notify-send "🈶 OCR Chinese (Speak)" "$FINAL"

if command -v wl-copy &>/dev/null; then
  echo -n "$FINAL" | wl-copy
elif command -v xclip &>/dev/null; then
  echo -n "$FINAL" | xclip -selection clipboard
fi

if command -v xdg-open &>/dev/null; then
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$CHINESE'''))")
  xdg-open "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=${ENCODED}" &>/dev/null &
fi

if command -v gtts-cli &>/dev/null; then
  gtts-cli "$CHINESE" -l zh-cn -o "$TMP_MP3" && mpv --really-quiet "$TMP_MP3"
else
  TTS_URL=$(python3 -c "import urllib.parse; print('https://translate.google.com/translate_tts?ie=UTF-8&tl=zh-CN&client=tw-ob&q=' + urllib.parse.quote('''$CHINESE'''))")
  curl -s -A "Mozilla/5.0" "$TTS_URL" -o "$TMP_MP3" || true
  if [ -s "$TMP_MP3" ]; then
    if command -v mpv &>/dev/null; then
      mpv --really-quiet "$TMP_MP3"
    elif command -v ffplay &>/dev/null; then
      ffplay -nodisp -autoexit "$TMP_MP3"
    fi
  fi
fi
