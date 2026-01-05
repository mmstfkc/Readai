from PIL import Image
import pytesseract
from .base import BaseExtractor

class ImageOCRExtractor(BaseExtractor):

    def extract(self, file_path: str) -> str:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image, lang="tur+eng")
