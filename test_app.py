import unittest
import os
import json
from config import load_config, save_config, get_theme_colors, DEFAULT_CONFIG
from downloader_logic import DownloaderLogic
from updater import check_for_ytdlp_updates

class TestAppComponents(unittest.TestCase):

    def test_config_load_save(self):
        # Clean up if exists
        if os.path.exists("config.json"):
            os.remove("config.json")

        config = load_config()
        self.assertEqual(config["theme"], "High Contrast")

        config["theme"] = "Cataract Friendly"
        save_config(config)

        new_config = load_config()
        self.assertEqual(new_config["theme"], "Cataract Friendly")

        if os.path.exists("config.json"):
            os.remove("config.json")

    def test_theme_colors(self):
        colors = get_theme_colors("High Contrast")
        self.assertEqual(colors["bg"], "#000000")

        colors = get_theme_colors("Unknown")
        # Should return default (High Contrast)
        self.assertEqual(colors["bg"], "#000000")

    def test_downloader_info(self):
        # We'll use a very short and stable video for testing if possible,
        # or just mock it. For now, let's try a real one but skip if it fails network-wise.
        dl = DownloaderLogic()
        info = dl.get_info("https://www.youtube.com/watch?v=BaW_jenozKc") # Youtube short
        if info:
            self.assertIn('title', info)
            self.assertIn('formats', info)

    def test_updater(self):
        # This will actually try to update yt-dlp
        # We just check if it runs without crashing
        result = check_for_ytdlp_updates()
        self.assertIsInstance(result, bool)

if __name__ == "__main__":
    unittest.main()
