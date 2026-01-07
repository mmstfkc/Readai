import os
import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import BaseLLM
from .prompts import NORMALIZE_OCR_TEXT_PROMPT
from .postfix import apply_postfix


def extract_first_json(text: str) -> dict:
    """
    Extract the first valid JSON object from LLM output.
    """
    matches = re.finditer(r"\{[\s\S]*?\}", text)
    for match in matches:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            continue
    raise ValueError("No valid JSON found")


class LocalLLM(BaseLLM):

    model_name = os.getenv("LLM_PUBLIC_NAME", "local-llm")

    def __init__(self):
        self.model_path = os.getenv("LOCAL_LLM_PATH", "/app/models/llm/current")
        if not os.path.isdir(self.model_path):
            raise RuntimeError(f"Local LLM path not found: {self.model_path}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            local_files_only=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
            local_files_only=True
        ).to(self.device)

        self.model.eval()

    def normalize_text(self, text: str) -> str:
        prompt = f"{NORMALIZE_OCR_TEXT_PROMPT}\n{text}"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.device)

        max_new_tokens=len(inputs["input_ids"][0]) + 300

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.0,
                do_sample=False,
                repetition_penalty=1.05,
                eos_token_id=self.tokenizer.eos_token_id
            )

        decoded = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )

        try:
            data = extract_first_json(decoded)
            cleaned_text = data.get("cleaned_text", "").strip()
            if cleaned_text:
                return apply_postfix(cleaned_text)
        except Exception:
            pass

        return apply_postfix(text)
