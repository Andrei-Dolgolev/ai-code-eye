from pathlib import Path
from typing import List
from rich.progress import Progress
from rich.console import Console
import openai
from .config import Settings
import re

console = Console()

class CodeTranslator:
    def __init__(self, settings: Settings):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.model_name
        
    def translate_code(self, code: str, source_lang: str, target_lang: str, file_name: str) -> (str, str):
        prompt = f"""You are a code translation assistant.

Translate the following {source_lang} code to {target_lang}. The code is from the file '{file_name}'.

Maintain the same functionality and structure, including class definitions and static methods.

For {target_lang} output:
- Convert Java classes to ES6 JavaScript classes
- Maintain method signatures and behavior
- Use modern JavaScript conventions
- Ensure that static methods in Java are also static in JavaScript
- Export classes properly for module usage

Provide a brief description of what this code does, followed by the translated code in a code block.

Important:
- Only translate the code provided.
- Do not include code from other files or any additional code not present in the input.
- Do not refer to or assume the existence of external classes or methods unless they are explicitly defined in the provided code.

{source_lang} code from '{file_name}':
{code}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code translation assistant who accurately translates code while maintaining functionality and proper class structure. Provide a brief description and the translated code. Ensure that only code from the provided input is translated."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2048
            )
            response_text = response.choices[0].message.content.strip()

            # Extract the translated code from the last code block
            code_snippets = re.findall(r'```(?:\w+)?\n(.*?)```', response_text, re.DOTALL)
            if code_snippets:
                translated_code = code_snippets[-1].strip()
                # Remove all code blocks to extract the description
                description = re.sub(r'```(?:\w+)?\n.*?```', '', response_text, flags=re.DOTALL).strip()
            else:
                translated_code = ''
                description = response_text.strip()

            return translated_code, description
        except Exception as e:
            console.print(f"[red]Error during translation: {str(e)}[/red]")
            raise

    def translate_project(self, source_dir: Path, output_dir: Path, 
                         source_ext: str, target_ext: str,
                         source_lang: str, target_lang: str) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        source_files = list(source_dir.rglob(f"*{source_ext}"))
        
        # Dictionary to hold descriptions for the project tree
        project_descriptions = {}

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

                # Directly translate the entire file without splitting
                translated_code, description = self.translate_code(
                    source_code, source_lang, target_lang, str(relative_path)
                )

                # Write the translated code to the output file
                if translated_code:
                    target_file.write_text(translated_code, encoding='utf-8')
                else:
                    console.print(f"[red]No translated code returned for {relative_path}[/red]")

                # Store the description in the project descriptions dictionary
                if description:
                    project_descriptions[str(relative_path)] = description.strip()

                progress.advance(task)

        # After translation, save the descriptions to a file
        self.save_project_descriptions(project_descriptions, output_dir)

    def save_project_descriptions(self, descriptions: dict, output_dir: Path):
        description_file = output_dir / 'project_descriptions.txt'
        with description_file.open('w', encoding='utf-8') as f:
            for file_path, description in descriptions.items():
                f.write(f"File: {file_path}\n")
                f.write(f"Description:\n{description}\n")
                f.write("-" * 40 + "\n")