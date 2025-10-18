#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.local/share/hanziocr"
BIN_DIR="$HOME/.local/bin"
WRAPPER="$BIN_DIR/hanziocr"
UNINSTALL_SCRIPT="$INSTALL_DIR/uninstall.sh"

echo "📦 Iniciando instalação do HanziOCR..."
sleep 0.5

# ============================================
# 🔍 Limpa resíduos de instalações antigas
# ============================================
if [ -d "$WRAPPER" ]; then
  echo "⚠️ Removendo diretório antigo em $WRAPPER..."
  rm -rf "$WRAPPER"
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

echo "📁 Diretórios garantidos:"
echo "  - Scripts: $INSTALL_DIR"
echo "  - Binário: $BIN_DIR"
sleep 0.5

# ============================================
# 📂 Copia scripts
# ============================================
echo "📁 Copiando scripts para $INSTALL_DIR..."
cp hanzi_*.sh hanzi_*.py "$INSTALL_DIR"/
chmod +x "$INSTALL_DIR"/hanzi_*
sleep 0.5

# ============================================
# ⚙️ Cria comando executável
# ============================================
echo "⚙️ Criando comando 'hanziocr' em $WRAPPER..."
sleep 0.5

printf '%s\n' '#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$HOME/.local/share/hanziocr"
case "${1:-}" in
  start|"") exec "$BASE_DIR/hanzi_capture.sh" ;;
  speak)    exec "$BASE_DIR/hanzi_capture_speak.sh" ;;
  replay)   exec "$BASE_DIR/hanzi_replay.sh" ;;
  kill|stop) exec "$BASE_DIR/hanzi_kill.sh" ;;
  tray)     exec python3 "$BASE_DIR/hanzi_ocr_tray.py" ;;
  server)   exec python3 "$BASE_DIR/hanzi_ocr_server.py" ;;
  *) echo "Uso: hanziocr {start|speak|replay|kill|tray|server}"; exit 1 ;;
esac' > "$WRAPPER"

chmod +x "$WRAPPER"
sleep 0.5

# ============================================
# 🧹 Cria desinstalador
# ============================================
echo "🧹 Criando desinstalador..."
sleep 0.5

printf '%s\n' '#!/usr/bin/env bash
set -euo pipefail
echo "🧹 Removendo HanziOCR..."
rm -rf "$HOME/.local/share/hanziocr"
rm -f "$HOME/.local/bin/hanziocr"
echo "✅ HanziOCR removido com sucesso!"
' > "$UNINSTALL_SCRIPT"

chmod +x "$UNINSTALL_SCRIPT"
sleep 0.5

# ============================================
# ✅ Conclusão
# ============================================
echo "✅ Instalação concluída!"
echo "📦 Scripts em: $INSTALL_DIR"
echo "⚙️ Comando disponível: hanziocr"
echo
echo "🧹 Para remover: bash $UNINSTALL_SCRIPT"
echo
echo "🎉 Execute: hanziocr start"
