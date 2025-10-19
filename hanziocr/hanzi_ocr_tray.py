#!/usr/bin/env python3
import os, signal, subprocess, time, threading
from PIL import Image, ImageDraw
import pystray

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = "/tmp/hanzi_ocr"
CACHE_DIR = os.path.expanduser("~/.cache/hanziocr")
SERVER_PID = os.path.join(TMP_DIR, "server.pid")
SERVER_SCRIPT = os.path.join(BASE_DIR, "hanzi_ocr_server.py")
LANG_FILE = os.path.join(TMP_DIR, "lang.conf")
HISTORY_FILE = os.path.join(CACHE_DIR, "history.log")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def make_icon(color):
    img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=color)
    return img

ICON_ON = make_icon((0, 210, 0, 255))     
ICON_OFF = make_icon((230, 60, 60, 255))  


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
    subprocess.Popen([
        "notify-send", "🌐 Hanzi OCR",
        f"Idioma alterado para {'Inglês 🇬🇧' if new_lang == 'en' else 'Português 🇧🇷'}"
    ])

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

def open_folder(icon=None, item=None):
    subprocess.Popen(["xdg-open", TMP_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def open_history(icon=None, item=None):
    """Abre o histórico de OCR no editor padrão"""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            f.write("📜 Histórico vazio.\n")
    subprocess.Popen(["xdg-open", HISTORY_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_capture(icon=None, item=None):
    subprocess.Popen(["bash", os.path.join(BASE_DIR, "hanzi_capture.sh")])

def run_speak(icon=None, item=None):
    subprocess.Popen(["bash", os.path.join(BASE_DIR, "hanzi_capture_speak.sh")])

def run_replay(icon=None, item=None):
    subprocess.Popen(["bash", os.path.join(BASE_DIR, "hanzi_replay.sh")])

def run_kill(icon=None, item=None):
    subprocess.Popen(["bash", os.path.join(BASE_DIR, "hanzi_kill.sh")])

def exit_tray(icon, item):
    try:
        stop_server()
    except Exception:
        pass
    subprocess.Popen(["notify-send", "👋 Hanzi OCR", "Tray encerrado."])
    icon.stop()

def refresh(icon):
    while True:
        running = server_running()
        lang = get_lang()
        icon.icon = ICON_ON if running else ICON_OFF
        icon.title = f"Hanzi OCR — {'Ativo 🟢' if running else 'Parado 🔴'}"

        lang_label = f"🌐 Idioma: {'Português 🇧🇷' if lang == 'pt' else 'Inglês 🇬🇧'}"

        menu_items = [
            pystray.MenuItem(lang_label, toggle_lang),
            pystray.MenuItem("📜 Ver histórico", open_history),
            pystray.MenuItem("📂 Pasta temporária", open_folder),
            pystray.MenuItem("🎥 Captura", run_capture),
            pystray.MenuItem("🔊 Speak", run_speak),
            pystray.MenuItem("♻️ Replay", run_replay),
            pystray.MenuItem("🧹 Kill All", run_kill),
            pystray.Menu.SEPARATOR,
        ]

        if running:
            menu_items.insert(0, pystray.MenuItem("🟥 Parar Servidor", stop_server))
            menu_items.append(pystray.MenuItem("🚪 Sair (encerra tudo)", lambda: exit_tray(icon, None)))
        else:
            menu_items.insert(0, pystray.MenuItem("🟩 Iniciar Servidor", start_server))
            menu_items.append(pystray.MenuItem("🚪 Sair", lambda: exit_tray(icon, None)))

        icon.menu = pystray.Menu(*menu_items)
        time.sleep(1.5)

def main():
    icon = pystray.Icon("hanzi_ocr", ICON_OFF, "Hanzi OCR — Parado 🔴")
    start_server()
    threading.Thread(target=refresh, args=(icon,), daemon=True).start()
    icon.run()

if __name__ == "__main__":
    main()
