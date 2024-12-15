from pathlib import Path
from typing import List
from rich.progress import Progress
from rich.console import Console
import openai
from .config import Settings

console = Console()

class CodeTranslator:
    def __init__(self, settings: Settings):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        
    def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        prompt = f"""Translate the following {source_lang} code to {target_lang}.
        Maintain the same functionality and structure, including class definitions and static methods.
        For JavaScript output:
        - Convert Java classes to ES6 JavaScript classes
        - Maintain method signatures and behavior
        - Use modern JavaScript conventions
        - Ensure that static methods in Java are also static in JavaScript
        - Export classes properly for module usage
        Only return the translated code without any explanations.
        
        {source_lang} code:
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code translation assistant. Translate code accurately while maintaining functionality and proper class structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"[red]Error during translation: {str(e)}[/red]")
            raise

    def split_into_chunks(self, code: str, max_chunk_size: int = 1000) -> List[str]:
        # Simple splitting by newlines for now
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > max_chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(line)
            current_size += line_size
            
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks

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