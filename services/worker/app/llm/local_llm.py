import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import BaseLLM
from .prompts import NORMALIZE_OCR_TEXT_PROMPT


class LocalLLM(BaseLLM):
    """
    Loads a local model from disk (no hub download at runtime).
    Model identity is intentionally not exposed.
    """

    model_name = os.getenv("LLM_PUBLIC_NAME", "local-llm")

    def __init__(self):
        self.model_path = os.getenv("LOCAL_LLM_PATH", "/app/models/llm/current")
        if not os.path.isdir(self.model_path):
            raise RuntimeError(f"Local LLM path not found: {self.model_path}")

        # If there is a GPU, use it
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            local_files_only=True
        )

        # Model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",  # Automatic mapping if GPU is available
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
            local_files_only=True
        )
        self.model.eval()

    def normalize_text(self, text: str) -> str:
        # Prompt: “editor” behavior
        prompt = (
            f"{NORMALIZE_OCR_TEXT_PROMPT}\n\n"
            f"OCR TEXT:\n{text}\n\n"
            f"CLEANED TEXT:\n"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=int(os.getenv("LLM_MAX_NEW_TOKENS", "800")),
                temperature=0.0,
                do_sample=False,
            )

        decoded = self.tokenizer.decode(out[0], skip_special_tokens=True)

        # only extract the CLEANED TEXT section
        if "CLEANED TEXT:" in decoded:
            return decoded.split("CLEANED TEXT:")[-1].strip()
        return decoded.strip()
