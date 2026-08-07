import argparse
import logging
from typing import Callable

from config import AppConfig
from adapters import ScreenCapturer, TextExtractor, GoogleTranslator
from processor import SubtitleProcessor
from ui import UIOverlay

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="de")
    parser.add_argument("--target", type=str, default="ru")
    parser.add_argument("--tess-lang", type=str, default="deu")

    args = parser.parse_args()

    config = AppConfig(
        source_lang=args.source,
        target_lang=args.target,
        tesseract_lang=args.tess_lang
    )

    capturer = ScreenCapturer(config)
    extractor = TextExtractor(config)
    translator = GoogleTranslator()

    def build_processor(update_callback: Callable[[str], None]) -> SubtitleProcessor:
        return SubtitleProcessor(capturer, extractor, translator, config, update_callback)

    app = UIOverlay(build_processor, config)
    app.run()


if __name__ == "__main__":
    main()
