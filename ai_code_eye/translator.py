from pathlib import Path
from typing import List, Optional
import openai
from rich.console import Console
from rich.progress import Progress
from .config import Settings
from .utils import estimate_tokens

console = Console()

class CodeTranslator:
    def __init__(self, settings: Settings):
        self.settings = settings
        openai.api_key = settings.openai_api_key

    def count_tokens(self, text: str) -> int:
        return estimate_tokens(text)

    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks based on token count."""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for line in text.split('\n'):
            line_tokens = self.count_tokens(line)
            if current_tokens + line_tokens > self.settings.chunk_size:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def translate_code(self, source_code: str, source_lang: str, target_lang: str) -> str:
        prompt = self.settings.get_translation_prompt(source_code, source_lang, target_lang)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.settings.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.settings.temperature,
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            console.print(f"[red]Error during translation: {e}[/red]")
            return ""

    def translate_project(self, source_dir: Path, output_dir: Path, 
                         source_ext: str, target_ext: str,
                         source_lang: str, target_lang: str) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        source_files = list(source_dir.rglob(f"*{source_ext}"))
        
        with Progress() as progress:
            task = progress.add_task(
                f"[green]Translating {source_lang} to {target_lang}...",
                total=len(source_files)
            )
            
            for source_file in source_files:
                relative_path = source_file.relative_to(source_dir)
                target_file = output_dir / relative_path.with_suffix(target_ext)
                
                console.print(f"\nTranslating: {relative_path}")
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                source_code = source_file.read_text(encoding='utf-8')
                chunks = self.split_into_chunks(source_code)
                
                translated_chunks = []
                for i, chunk in enumerate(chunks, 1):
                    console.print(f"  Processing chunk {i}/{len(chunks)}")
                    translated_chunk = self.translate_code(chunk, source_lang, target_lang)
                    translated_chunks.append(translated_chunk)
                
                target_file.write_text('\n'.join(translated_chunks), encoding='utf-8')
                progress.advance(task) 