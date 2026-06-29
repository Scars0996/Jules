import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "download_path": str(Path.home() / "Downloads"),
    "converter_path": str(Path.home() / "Downloads" / "Converted"),
    "theme": "Contraste Élevé",
    "font_scale": 2.0,
    "auto_update_ytdlp": True,
    "download_mode": "Single", # Single or Playlist
    "auto_download": False,
    "saved_quality": "best",
    "saved_format": "mp4"
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
        "Contraste Élevé": {
            "bg": "#000000",
            "fg": "#FFFFFF",
            "button_bg": "#444444",
            "button_fg": "#FFFFFF",
            "accent": "#FFFF00",
            "font_family": "Arial Black",
            "paste_btn": "#28A745",
            "delete_btn": "#DC3545",
            "download_btn": "#6F42C1"
        },
        "Texte Large Clair": {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "button_bg": "#E0E0E0",
            "button_fg": "#000000",
            "accent": "#0000FF",
            "font_family": "Verdana",
            "paste_btn": "#28A745",
            "delete_btn": "#DC3545",
            "download_btn": "#6F42C1"
        },
         "Spécial Cataracte": {
            "bg": "#FFFFE0", # Light Yellow background often better for some cataracts
            "fg": "#000000",
            "button_bg": "#C0C0C0",
            "button_fg": "#000000",
            "accent": "#800000",
            "font_family": "Arial",
            "paste_btn": "#28A745",
            "delete_btn": "#DC3545",
            "download_btn": "#6F42C1"
        }
    }
    return themes.get(theme_name, themes["Contraste Élevé"])
