import difflib
import time
from typing import Callable
from adapters import ScreenCapturer, TextExtractor, GoogleTranslator
from config import AppConfig


class SubtitleProcessor:
    def __init__(
            self,
            capturer: ScreenCapturer,
            extractor: TextExtractor,
            translator: GoogleTranslator,
            config: AppConfig,
            on_text_update: Callable[[str], None]
    ):
        self.capturer = capturer
        self.extractor = extractor
        self.translator = translator
        self.config = config
        self.on_text_update = on_text_update
        self.last_text = ""
        self._running = False
        self.is_paused = False

    def start(self):
        self._running = True
        while self._running:
            self._process_frame()
            time.sleep(0.1)

    def stop(self):
        self._running = False

    def _process_frame(self):
        if self.is_paused:
            return

        img = self.capturer.capture()
        text = self.extractor.extract(img)

        if text and len(text) > 2:
            similarity = difflib.SequenceMatcher(None, text, self.last_text).ratio()

            if similarity < 0.85:
                translated_text = self.translator.translate(
                    text=text,
                    source_lang=self.config.source_lang,
                    target_lang=self.config.target_lang
                )
                self.on_text_update(f" {text}\n {translated_text}")
                self.last_text = text
