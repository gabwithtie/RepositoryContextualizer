import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".code_rag_config.json"

DEFAULT_SETTINGS = {
    "target_dir": ".",
    "top_k": 5,
    "output_file": "packed_context.txt",
    "extensions": [".py", ".ts", ".js", ".rs", ".go", ".cpp", ".c", ".h", ".md", ".json", ".sql", ".yaml", ".html", ".css"]
}

def load_settings() -> dict:
    """Load settings from JSON config file or return defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_settings = json.load(f)
                # Merge defaults with saved settings in case new keys exist
                return {**DEFAULT_SETTINGS, **user_settings}
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """Save dictionary settings to the user's home directory."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Failed to save settings: {e}")