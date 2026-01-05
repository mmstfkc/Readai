from abc import ABC, abstractmethod

class BaseLLM(ABC):

    @abstractmethod
    def normalize_text(self, text: str) -> str:
        pass
