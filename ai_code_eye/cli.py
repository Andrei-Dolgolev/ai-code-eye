from pathlib import Path
import typer
from rich.console import Console
from .translator import CodeTranslator
from .config import Settings

app = typer.Typer()
console = Console()

@app.command()
def translate(
    source_dir: Path = typer.Argument(..., help="Source code directory"),
    output_dir: Path = typer.Argument(..., help="Output directory for translated code"),
    source_lang: str = typer.Option("java", help="Source language"),
    target_lang: str = typer.Option("javascript", help="Target language"),
    source_ext: str = typer.Option(".java", help="Source file extension"),
    target_ext: str = typer.Option(".js", help="Target file extension"),
    model: str = typer.Option("gpt-4", help="OpenAI model to use"),
):
    """
    Translate code from one programming language to another using AI.
    """
    if not source_dir.exists():
        console.print(f"[red]Error: Source directory '{source_dir}' does not exist.[/red]")
        raise typer.Exit(1)

    settings = Settings(model_name=model)
    if not settings.openai_api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable is not set.[/red]")
        raise typer.Exit(1)

    translator = CodeTranslator(settings)
    
    try:
        translator.translate_project(
            source_dir=source_dir,
            output_dir=output_dir,
            source_ext=source_ext,
            target_ext=target_ext,
            source_lang=source_lang,
            target_lang=target_lang,
        )
        console.print("[green]Translation completed successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error during translation: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 