from dataclasses import dataclass

LANGUAGES = {
    "🇬🇧 English": {"source": "en", "target": "en", "tess": "eng"},
    "🇩🇪 Deutsch": {"source": "de", "target": "de", "tess": "deu"},
    "🇺🇦 Українська": {"source": "uk", "target": "uk", "tess": "ukr"},
    "🏴 Русский": {"source": "ru", "target": "ru", "tess": "rus"},
    "🇪🇸 Español": {"source": "es", "target": "es", "tess": "spa"},
    "🇫🇷 Français": {"source": "fr", "target": "fr", "tess": "fra"},
    "🇮🇹 Italiano": {"source": "it", "target": "it", "tess": "ita"},
    "🇨🇳 中文": {"source": "zh-CN", "target": "zh-CN", "tess": "chi_sim"},
    "🇯🇵 日本語": {"source": "ja", "target": "ja", "tess": "jpn"},
    "🇵🇹 Português": {"source": "pt", "target": "pt", "tess": "por"}
}

@dataclass
class AppConfig:
    source_lang: str
    target_lang: str
    tesseract_lang: str
    monitor_top: int = 571
    monitor_left: int = 360
    monitor_width: int = 712
    monitor_height: int = 166

    @property
    def monitor_rect(self) -> dict:
        return {
            "top": self.monitor_top,
            "left": self.monitor_left,
            "width": self.monitor_width,
            "height": self.monitor_height
        }