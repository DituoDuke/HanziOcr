#!/usr/bin/env python3
import os, signal, subprocess, time, threading
from PIL import Image, ImageDraw
import pystray

TMP_DIR = "/tmp/hanzi_ocr"
SERVER_PID = os.path.join(TMP_DIR, "server.pid")
SERVER_SCRIPT = os.path.expanduser("~/.local/bin/hanzi_ocr_server.py")
LANG_FILE = os.path.join(TMP_DIR, "lang.conf")
os.makedirs(TMP_DIR, exist_ok=True)

# === ícones coloridos visíveis no Wayland ===
def make_icon(color):
    img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=color)
    return img

ICON_ON = make_icon((0, 210, 0, 255))     # 🟢 ativo
ICON_OFF = make_icon((230, 60, 60, 255))  # 🔴 parado

# === idioma atual e alternância ===
def get_lang():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE) as f:
            lang = f.read().strip()
            if lang in ("pt", "en"):
                return lang
    return "pt"

def toggle_lang(icon=None, item=None):
    current = get_lang()
    new_lang = "en" if current == "pt" else "pt"
    with open(LANG_FILE, "w") as f:
        f.write(new_lang)
    subprocess.Popen(["notify-send", "🌐 Hanzi OCR", f"Idioma alterado para {'Inglês 🇬🇧' if new_lang == 'en' else 'Português 🇧🇷'}"])

# === verifica se o servidor está rodando ===
def server_running():
    if not os.path.exists(SERVER_PID):
        return False
    try:
        with open(SERVER_PID) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except Exception:
        return False

# === iniciar servidor ===
def start_server(icon=None, item=None):
    if server_running():
        return
    subprocess.Popen(
        ["python3", SERVER_SCRIPT],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    subprocess.Popen(["notify-send", "🟢 Hanzi OCR", "Servidor iniciado."])
    time.sleep(1)

# === parar servidor ===
def stop_server(icon=None, item=None):
    if not server_running():
        return
    try:
        with open(SERVER_PID) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(SERVER_PID)
        subprocess.Popen(["notify-send", "🔴 Hanzi OCR", "Servidor encerrado."])
    except Exception:
        pass

# === abrir pasta temporária ===
def open_folder(icon=None, item=None):
    subprocess.Popen(["xdg-open", TMP_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# === executar scripts utilitários ===
def run_capture(icon=None, item=None):
    subprocess.Popen(["bash", os.path.expanduser("~/.local/bin/hanzi_capture.sh")])

def run_speak(icon=None, item=None):
    subprocess.Popen(["bash", os.path.expanduser("~/.local/bin/hanzi_speak.sh")])

def run_replay(icon=None, item=None):
    subprocess.Popen(["bash", os.path.expanduser("~/.local/bin/hanzi_replay.sh")])

# === sair do tray ===
def exit_tray(icon, item):
    try:
        stop_server()
    except Exception:
        pass
    subprocess.Popen(["notify-send", "👋 Hanzi OCR", "Tray encerrado."])
    icon.stop()

# === atualiza ícone e menu dinamicamente ===
def refresh(icon):
    while True:
        running = server_running()
        lang = get_lang()
        icon.icon = ICON_ON if running else ICON_OFF
        icon.title = f"Hanzi OCR — {'Ativo 🟢' if running else 'Parado 🔴'}"

        lang_label = f"🌐 Idioma: {'Português 🇧🇷' if lang == 'pt' else 'Inglês 🇬🇧'}"

        if running:
            icon.menu = pystray.Menu(
                pystray.MenuItem("🟥 Parar Servidor", stop_server),
                pystray.MenuItem(lang_label, toggle_lang),
                pystray.MenuItem("📂 Abrir Pasta OCR", open_folder),
                pystray.MenuItem("🎥 Captura", run_capture),
                pystray.MenuItem("🔊 Speak", run_speak),
                pystray.MenuItem("♻️ Replay", run_replay),
                pystray.MenuItem("🚪 Sair (encerra tudo)", lambda: exit_tray(icon, None)),
            )
        else:
            icon.menu = pystray.Menu(
                pystray.MenuItem("🟩 Iniciar Servidor", start_server),
                pystray.MenuItem(lang_label, toggle_lang),
                pystray.MenuItem("📂 Abrir Pasta OCR", open_folder),
                pystray.MenuItem("🎥 Captura", run_capture),
                pystray.MenuItem("🔊 Speak", run_speak),
                pystray.MenuItem("♻️ Replay", run_replay),
                pystray.MenuItem("🚪 Sair", lambda: exit_tray(icon, None)),
            )
        time.sleep(1.5)

# === inicia o tray e servidor junto ===
def main():
    icon = pystray.Icon("hanzi_ocr", ICON_OFF, "Hanzi OCR — Parado 🔴")
    start_server()
    threading.Thread(target=refresh, args=(icon,), daemon=True).start()
    icon.run()

if __name__ == "__main__":
    main()
