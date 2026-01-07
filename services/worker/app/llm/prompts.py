NORMALIZE_OCR_TEXT_PROMPT = """
TASK:
You will be given OCR-extracted text.

INSTRUCTIONS (STRICT):
- Fix spelling and broken words caused by OCR
- Merge lines where appropriate
- Preserve the original meaning and structure
- Preserve all numbers, dates and monetary values EXACTLY
- Do NOT add explanations
- Do NOT add comments
- Do NOT add summaries
- Do NOT add any text that was not present in the OCR input

OUTPUT RULES (MANDATORY):
- Output ONLY the cleaned text
- Do NOT repeat the input
- Do NOT include titles, headings or labels
- Do NOT explain what you changed
- Do NOT include phrases like "This document", "OCR", "we fixed", etc.

If you violate any rule, the output is invalid.
"""
