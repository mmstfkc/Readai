from .base import BaseLLM

class MockLLM(BaseLLM):
    model_name = "mock-llm"

    def normalize_text(self, text: str) -> str:
        # TEMP: gerçek LLM yerine placeholder
        return text.replace("  ", " ").strip()
