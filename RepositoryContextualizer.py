import sys
import multiprocessing

# Prevents infinite subprocess loops with PyTorch/ChromaDB under PyInstaller
if __name__ == "__main__":
    multiprocessing.freeze_support()

import typer
from rich.console import Console
from modules.scanner import scan_directory
from modules.indexer import VectorIndex
from modules.packer import pack_context

app = typer.Typer(help="Code-RAG: File indexing and context gatherer for LLMs.")
console = Console()

def close_splash():
    """Closes the PyInstaller splash screen if active."""
    try:
        import pyi_splash
        if pyi_splash.is_alive():
            pyi_splash.close()
    except ImportError:
        pass

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Default entry point. If no command is provided (e.g. double-clicking the EXE),
    launch the GUI interface automatically.
    """
    if ctx.invoked_subcommand is None:
        from app_gui.window import launch_gui
        launch_gui()

@app.command()
def query(
    user_query: str = typer.Argument(..., help="The query/question to find relevant code for."),
    root_dir: str = typer.Option(".", "--dir", "-d", help="Directory to scan."),
    top_k: int = typer.Option(5, "--top", "-k", help="Number of code chunks to retrieve."),
    output_file: str = typer.Option("packed_context.txt", "--output", "-o", help="Output file path.")
):
    """Index codebase and pack relevant files for an AI query via CLI."""
    close_splash()
    files = scan_directory(root_dir, extensions={".py", ".cs", ".js", ".ts", ".md"})
    index = VectorIndex(cache_dir=f"{root_dir}/.rag_cache")
    index.index_files(files)
    results = index.search(user_query, top_k=top_k)
    pack_context(results, user_query, output_file)

@app.command()
def gui():
    """Explicitly launch the GUI desktop interface."""
    from app_gui.window import launch_gui
    launch_gui()

if __name__ == "__main__":
    app()