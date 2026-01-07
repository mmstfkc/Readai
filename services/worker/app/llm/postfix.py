import re
from typing import Dict


# 🔒 Domain-specific, HIGH-CONFIDENCE OCR fixes
POST_FIX_MAP: Dict[str, str] = {
    # Turkish character losses
    "amaçlndnr": "amaçlıdır",
    "amaçlndr": "amaçlıdır",
    "Yalnnz": "Yalnız",
    "Yalnnz": "Yalnız",
    "Dannnmanlnk": "Danışmanlık",
    "nnleme": "İnceleme",
    "nstanbul": "İstanbul",
    "ninli": "Şişli",

    # Common OCR junk
    " A.n.": " A.Ş.",
    "A.n.": "A.Ş.",
}


def apply_postfix(text: str) -> str:
    """
    Apply deterministic OCR post-fixes.
    Only exact, high-confidence replacements are applied.
    """
    fixed_text = text

    for wrong, correct in POST_FIX_MAP.items():
        # Word-boundary aware replace when possible
        pattern = r"\b" + re.escape(wrong) + r"\b"
        fixed_text = re.sub(pattern, correct, fixed_text)

    return fixed_text
