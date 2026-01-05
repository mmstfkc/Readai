import os
from .pdf_extractor import PdfTextExtractor
from .image_extractor import ImageOCRExtractor
from .text_extractor import TextExtractor

class ExtractorDispatcher:

    def __init__(self):
        self.pdf_extractor = PdfTextExtractor()
        self.image_extractor = ImageOCRExtractor()
        self.text_extractor = TextExtractor()

    def extract(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self.pdf_extractor.extract(file_path)

        if ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            return self.image_extractor.extract(file_path)

        if ext in [".txt"]:
            return self.text_extractor.extract(file_path)

        raise ValueError(f"Unsupported file type: {ext}")
