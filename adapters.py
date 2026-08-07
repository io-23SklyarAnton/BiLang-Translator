import os
import sys
import cv2
import mss
import numpy as np
import pytesseract
import requests
import logging
from config import AppConfig

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    default_tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_tess_path):
        pytesseract.pytesseract.tesseract_cmd = default_tess_path


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
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "Translation error"
