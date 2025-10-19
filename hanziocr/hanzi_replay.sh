#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(dirname "$0")"

TMP_DIR="/tmp/hanzi_ocr"
RES_FILE="$TMP_DIR/response.json"
TMP_MP3="$TMP_DIR/replay_tts.mp3"

if [ ! -s "$RES_FILE" ]; then
  notify-send "🔁 Replay OCR" "Nenhum resultado anterior encontrado."
  exit 1
fi

CHINESE=$(jq -r '.chinese' "$RES_FILE")
PINYIN=$(jq -r '.pinyin' "$RES_FILE")
TRANSLATION=$(jq -r '.english // .portuguese' "$RES_FILE")
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$CHINESE'''))")
MDBG="https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=${ENCODED}"

FINAL="Chinese: $CHINESE
Pinyin: $PINYIN
Translation: $TRANSLATION"

if command -v wl-copy &>/dev/null; then
  echo -n "$FINAL" | wl-copy
elif command -v xclip &>/dev/null; then
  echo -n "$FINAL" | xclip -selection clipboard
fi

(
  response=$(timeout 30s notify-send --action 'open_url=MDBG' '🈶 Replay OCR' "$FINAL")
  case "$response" in
      "open_url")
          if command -v xdg-open &>/dev/null; then
            xdg-open "$MDBG"
          fi
          ;;
      *)
          ;;
  esac
) & disown


if [ -n "$CHINESE" ] && [ "$CHINESE" != "(nenhum texto detectado)" ]; then
  (
    if command -v gtts-cli &>/dev/null; then
      gtts-cli "$CHINESE" -l zh -o "$TMP_MP3" && mpv --really-quiet "$TMP_MP3"
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
  ) & disown
fi

