#!/usr/bin/env python3
import os
import json
import time
import subprocess
from paddleocr import PaddleOCR
import jieba
from pypinyin import pinyin, Style

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TMP_DIR = "/tmp/hanzi_ocr"
REQ_FILE = os.path.join(TMP_DIR, "request.json")
RES_FILE = os.path.join(TMP_DIR, "response.json")
PID_FILE = os.path.join(TMP_DIR, "server.pid")
LANG_FILE = os.path.join(TMP_DIR, "lang.conf")

os.makedirs(TMP_DIR, exist_ok=True)
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))
    
def safe_init_ocr():
    """Inicializa o PaddleOCR (versão >=3.3.0, compatível e silenciosa)."""
    try:
        print("🈶 Inicializando PaddleOCR...")
        try:
            from paddleocr.tools.infer import utility
            utility.disable_log()
        except Exception:
            pass 

        ocr = PaddleOCR(
            lang='ch',
            use_textline_orientation=True,
            device='gpu'  # troca sozinho pra cpu caso sua gpu não tenha suporte, ou não possui o paddlepaddle certo instalado
        )
        return ocr
    except Exception as e:
        print(f"⚠️ Falha ao inicializar OCR: {e}")
        return None


def make_pinyin(text):
    """Gera pinyin com acentuação (jieba + pypinyin)."""
    jieba.setLogLevel(20)
    words = jieba.lcut(text, cut_all=False)
    punct = set("，。！？、,.;:!?;：()（）「」『』“”\"'—…·《》[]")
    parts = []
    for w in words:
        if not w.strip():
            continue
        if all(ch in punct for ch in w):
            parts.append(w)
        else:
            pys = pinyin(w, style=Style.TONE, heteronym=False)
            parts.append(f"{w} ({' '.join(s[0] for s in pys)})")
    return " ".join(parts)


def get_target_lang():
    """Lê o idioma alvo (pt/en)."""
    try:
        with open(LANG_FILE) as f:
            lang = f.read().strip()
            if lang in ("en", "pt"):
                return lang
    except FileNotFoundError:
        pass
    return "pt"


def translate_text(text, target_lang):
    """Traduz o texto usando translate-shell ou fallback online."""
    try:
        return subprocess.check_output(
            ["trans", "-b", f"zh:{target_lang}", text],
            text=True
        ).strip()
    except Exception:
        try:
            from deep_translator import GoogleTranslator
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e2:
            print(f"⚠️ Tradução falhou: {e2}")
            return "(sem tradução)"

ocr = safe_init_ocr()
if not ocr:
    print("🚫 Nenhum OCR disponível (falha total). O servidor ainda responderá, mas sem OCR.")
else:
    print("🈶 Servidor OCR pronto.")

while True:
    if os.path.exists(REQ_FILE):
        try:
            with open(REQ_FILE) as f:
                data = json.load(f)

            img_path = data.get("image")
            if not img_path or not os.path.exists(img_path):
                time.sleep(1)
                continue

            print(f"📸 Processando: {img_path}")
            text = "(erro no OCR)"

            if ocr:
                try:
                    result = ocr.predict(img_path)
                    texts = []
                    for page in result:
                        texts.extend(page.get("rec_texts", []))
                    text = "".join(texts).strip() or "(nenhum texto detectado)"
                except Exception as e:
                    print(f"⚠️ Erro no OCR: {e}")

            pin = make_pinyin(text)
            target_lang = get_target_lang()
            trans = translate_text(text, target_lang)
            label = "english" if target_lang == "en" else "portuguese"

            res = {
                "chinese": text,
                "pinyin": pin,
                label: trans
            }

            with open(RES_FILE, "w") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)

            print(f"✅ OCR completo: {text}")

            try:
                os.remove(REQ_FILE)
            except FileNotFoundError:
                pass

        except Exception as e:
            print(f"❌ Erro no servidor: {e}")

        time.sleep(2)

    time.sleep(1)
