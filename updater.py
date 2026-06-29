import os
import sys
import subprocess
import logging
import urllib.request
import platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_frozen():
    return getattr(sys, 'frozen', False)

def check_for_ytdlp_updates():
    """
    Checks and updates yt-dlp.
    If running as a script, uses pip.
    If running as a frozen EXE, it should ideally download the latest binary.
    """
    logger.info("Checking for yt-dlp updates...")

    if not is_frozen():
        try:
            # For the python module version
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            logger.info("yt-dlp is up to date (via pip).")
            return True
        except Exception as e:
            logger.error(f"Failed to update yt-dlp via pip: {e}")
            return False
    else:
        # If frozen (EXE), we might want to use yt-dlp's own update mechanism if it's available
        # or download the latest yt-dlp.exe from GitHub.
        # yt-dlp --update is a thing.
        try:
            # Try running the bundled yt-dlp with --update
            # This depends on how it was bundled.
            subprocess.check_call(["yt-dlp", "--update"])
            logger.info("yt-dlp updated itself.")
            return True
        except Exception as e:
            logger.error(f"Failed to self-update yt-dlp: {e}")
            return False

if __name__ == "__main__":
    check_for_ytdlp_updates()
