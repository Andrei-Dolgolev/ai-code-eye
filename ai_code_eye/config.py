from pydantic import BaseModel
from typing import Optional
import os

class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = "gpt-4"
    chunk_size: int = 3000
    temperature: float = 0.0
    
    def get_translation_prompt(self, code: str, source_lang: str, target_lang: str) -> str:
        return (
            f"You are a code conversion assistant. Convert the following {source_lang} "
            f"code to {target_lang}. Preserve logic and structure, but adjust "
            f"language-specific details as needed:\n\n{code}"
        ) 