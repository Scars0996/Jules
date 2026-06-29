import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "download_path": str(Path.home() / "Downloads"),
    "converter_path": str(Path.home() / "Downloads" / "Converted"),
    "theme": "High Contrast",
    "font_scale": 2.0,
    "auto_update_ytdlp": True
}

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Merge with default to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_theme_colors(theme_name):
    themes = {
        "High Contrast": {
            "bg": "#000000",
            "fg": "#FFFFFF",
            "button_bg": "#333333",
            "button_fg": "#FFFFFF",
            "accent": "#FFFF00",
            "font_family": "Arial"
        },
        "Large Text Light": {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "button_bg": "#E0E0E0",
            "button_fg": "#000000",
            "accent": "#0000FF",
            "font_family": "Verdana"
        },
         "Cataract Friendly": {
            "bg": "#FFFFE0", # Light Yellow background often better for some cataracts
            "fg": "#000000",
            "button_bg": "#C0C0C0",
            "button_fg": "#000000",
            "accent": "#800000",
            "font_family": "Arial"
        }
    }
    return themes.get(theme_name, themes["High Contrast"])
