from .base import BaseExtractor

class TextExtractor(BaseExtractor):

    def extract(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
