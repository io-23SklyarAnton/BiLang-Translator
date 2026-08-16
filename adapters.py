import os
import sys
import cv2
import mss
import numpy as np
import pytesseract
import requests
from config import AppConfig, CURRENT_SYSTEM


def _get_tesseract_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    if CURRENT_SYSTEM.is_windows():
        return os.path.join(base_path, "Tesseract-OCR", "tesseract.exe")
    elif CURRENT_SYSTEM.is_macos():
        return os.path.join(base_path, "Tesseract-mac", "tesseract")

    return "tesseract"


tess_path = _get_tesseract_path()
if os.path.exists(tess_path):
    pytesseract.pytesseract.tesseract_cmd = tess_path
    tessdata_prefix = os.path.join(os.path.dirname(tess_path), "tessdata")
    os.environ["TESSDATA_PREFIX"] = tessdata_prefix


class ScreenCapturer:
    def __init__(self, config: AppConfig):
        self.config = config
        self.sct = mss.mss()

    def capture(self) -> np.ndarray:
        return np.array(self.sct.grab(self.config.monitor_rect))


class TextExtractor:
    def __init__(self, config: AppConfig):
        self.config = config

    def extract(self, image: np.ndarray) -> str:
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        raw_text = pytesseract.image_to_string(
            thresh, lang=self.config.tesseract_lang, config='--psm 6'
        )
        return raw_text.replace('\n', ' ').strip()


class GoogleTranslator:
    API_URL = "https://translate.googleapis.com/translate_a/single"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return ""

        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }

        try:
            res = requests.get(self.API_URL, params=params, timeout=5).json()
            return "".join([x[0] for x in res[0]])
        except Exception:
            return "Translation error"
