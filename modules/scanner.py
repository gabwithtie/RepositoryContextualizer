import os
from pathlib import Path
import pathspec

def get_gitignore_spec(root_dir: str) -> pathspec.PathSpec:
    """Parses .gitignore if present in the target directory."""
    gitignore_path = Path(root_dir) / ".gitignore"
    patterns = [".git/", ".rag_cache/", "__pycache__/", "*.pyc", "*.exe", "*.dll", "*.so"]
    
    if gitignore_path.is_file():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns.extend(f.readlines())
            
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def scan_directory(root_dir: str, extensions: set[str]) -> list[Path]:
    """Scans for valid source files matching the user-selected extensions."""
    root = Path(root_dir).resolve()
    spec = get_gitignore_spec(str(root))
    matched_files = []

    # Ensure extensions formatted as lower-case with dot (e.g., '.py')
    valid_exts = {e if e.startswith(".") else f".{e}" for e in extensions}

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in valid_exts:
            try:
                rel_path = str(path.relative_to(root))
                if not spec.match_file(rel_path):
                    matched_files.append(path)
            except ValueError:
                continue

    return matched_files