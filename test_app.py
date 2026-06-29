import unittest
import os
import json
from config import load_config, save_config, get_theme_colors, DEFAULT_CONFIG
from downloader_logic import DownloaderLogic
from updater import check_for_ytdlp_updates

class TestAppComponents(unittest.TestCase):

    def test_config_load_save(self):
        if os.path.exists("config.json"):
            os.remove("config.json")

        config = load_config()
        self.assertEqual(config["theme"], "Contraste Élevé")
        self.assertEqual(config["download_mode"], "Single")

        config["download_mode"] = "Playlist"
        config["auto_download"] = True
        save_config(config)

        new_config = load_config()
        self.assertEqual(new_config["download_mode"], "Playlist")
        self.assertTrue(new_config["auto_download"])

        if os.path.exists("config.json"):
            os.remove("config.json")

    def test_theme_colors_localized(self):
        colors = get_theme_colors("Contraste Élevé")
        self.assertEqual(colors["bg"], "#000000")
        self.assertEqual(colors["paste_btn"], "#28A745")

        colors = get_theme_colors("Unknown")
        self.assertEqual(colors["bg"], "#000000")

    def test_downloader_cleanup_logic(self):
        from downloader_logic import DownloadTask
        # dl = DownloaderLogic()
        # Simulate a task
        test_file = "test_download.mp4"
        task = DownloadTask(None, None, ".", "Single", None, None)
        task.current_files = [test_file]

        # Create a fake partial file
        with open(test_file + ".part", "w") as f:
            f.write("partial data")

        self.assertTrue(os.path.exists(test_file + ".part"))
        task.cleanup_incomplete_files()
        self.assertFalse(os.path.exists(test_file + ".part"))

if __name__ == "__main__":
    unittest.main()
