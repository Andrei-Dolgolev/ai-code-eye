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
        
    def translate_code(self, code: str, source_lang: str, target_lang: str, file_name: str, project_structure: str) -> (str, str):
        dependencies_info = get_file_dependencies(code)
        file_name_with_js_extension = str(Path(file_name).with_suffix('.js'))
        
        prompt = f"""You are an expert code translator specializing in converting Java code to modern ES6 JavaScript. 

Translate the following {source_lang} code to {target_lang}. The code is from the file '{file_name}'. This file is part of a larger project with the following structure:

{project_structure}

Maintain the same functionality and structure, including class definitions, method signatures, and access modifiers. Ensure that the translated code integrates seamlessly with the rest of the project.

**Instructions for {target_lang} code**:
- Convert Java classes to ES6 classes using the `class` syntax.
- Use proper `import` and `export` statements to handle dependencies between modules.
- Replace Java-specific libraries and APIs with appropriate JavaScript or Web APIs.
- Maintain static methods and properties appropriately.
- Use modern JavaScript conventions (e.g., arrow functions, template literals) where suitable.
- Ensure that all methods and properties are correctly bound, especially when using `this`.
- **Adjust canvas initialization and rendering logic to use the HTML5 Canvas API, ensuring the canvas element and context are properly set up.**
- **Handle event listeners appropriately, binding them with the correct context to maintain 'this' references.**
- Include necessary constructors and super() calls if inheritance is involved.
- **Translate Java's exception handling (`try`, `catch`, `finally`, `throws`) appropriately to JavaScript, ensuring that all potential errors are properly managed.**
- **Adapt multithreaded or asynchronous Java code using JavaScript's asynchronous patterns (e.g., Promises, async/await), ensuring non-blocking operations.**
- **For Java interfaces and abstract classes, convert them into JavaScript classes or use ES6 class inheritance, and provide implementations for all abstract methods.**
- **Translate Java's static variables (especially `final` constants) to JavaScript's `const` or static class properties as appropriate.**
- **Maintain the project's module structure, ensuring that namespaces or packages are appropriately translated using ES6 modules.**
- **While JavaScript is dynamically typed, ensure that variable and method usages remain consistent. If necessary, include JSDoc comments to describe types for better readability and maintainability.**
- **Replace any third-party Java libraries with suitable JavaScript libraries or provide placeholders/comments where manual adjustment is needed.**
- **After translation, ensure that the code includes necessary setup for testing or includes comments on how to test the functionality.**
- **Modify GUI interactions and system resource access to utilize appropriate web APIs suitable for a browser environment.**

**Important**:
- Only translate the code provided in the 'Code to Translate' section.
- Do not include code from other files unless it's necessary for context and is specified in the 'Dependencies' section.
- If external classes or methods from other files are referenced, assume they have been translated similarly and import them accordingly.
- Do not add any additional functionality or logic not present in the original code.
- **Ensure that the translated code is functional within a JavaScript environment, making necessary adjustments for environment-specific logic.**
- **Address any Java-specific constructs that do not have direct equivalents in JavaScript, adapting them appropriately to maintain functionality.**

**Code to Translate ({source_lang} code from '{file_name}')**:
{code}

**Dependencies**:
{dependencies_info}

**Output**:
- First, provide a brief description of what this code does.
- Then, provide the translated code in a code block, specifying the language (JavaScript) and the file name, like so:

\`\`\`javascript:{file_name_with_js_extension}
// Translated code here
\`\`\`

Do not include any additional explanations outside the code block.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code translator who produces accurate and functional code translations while maintaining project structure and dependencies, class structure, method signatures."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            response_text = response.choices[0].message.content.strip()

            # Extract the translated code from the code block with the file name
            code_pattern = rf'```javascript:{re.escape(file_name_with_js_extension)}\n(.*?)```'
            match = re.search(code_pattern, response_text, re.DOTALL)
            if match:
                translated_code = match.group(1).strip()
            else:
                # Fallback to extract any JavaScript code block
                code_snippets = re.findall(r'```javascript\n(.*?)```', response_text, re.DOTALL)
                translated_code = code_snippets[-1].strip() if code_snippets else ''

            # Remove code blocks to extract the description
            description = re.sub(r'```.*?```', '', response_text, flags=re.DOTALL).strip()

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
                    source_code, source_lang, target_lang, str(relative_path), get_project_structure(source_dir)
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

def get_project_structure(source_dir: Path) -> str:
    structure = ""
    for path in sorted(source_dir.rglob("*.java")):
        relative_path = path.relative_to(source_dir)
        structure += f"- {relative_path}\n"
    return structure

def get_file_dependencies(code: str) -> str:
    # Simple regex to find import statements (can be enhanced)
    imports = re.findall(r'import\s+([a-zA-Z0-9_.]+);', code)
    dependencies = ""
    for imp in imports:
        dependencies += f"- {imp}\n"
    return dependencies if dependencies else "None"