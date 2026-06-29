import yt_dlp
import threading
import os
import logging

logger = logging.getLogger(__name__)

class DownloaderLogic:
    def __init__(self, progress_callback=None, finished_callback=None):
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.is_cancelled = False

    def get_info(self, url):
        """Fetches metadata and available formats for a given URL."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"Error fetching info: {e}")
            return None

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if self.progress_callback:
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%').replace('%','')
                try:
                    percent = float(p)
                except:
                    percent = 0.0
                self.progress_callback(percent, d.get('_speed_str', 'N/A'), d.get('_eta_str', 'N/A'))
            elif d['status'] == 'finished':
                self.progress_callback(100.0, "0", "0")

    def download(self, url, format_id, download_path):
        def run():
            ydl_opts = {
                'format': format_id if format_id else 'best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                if self.finished_callback:
                    self.finished_callback(True, "Download Completed")
            except Exception as e:
                logger.error(f"Download error: {e}")
                if self.finished_callback:
                    self.finished_callback(False, str(e))

        self.is_cancelled = False
        thread = threading.Thread(target=run)
        thread.start()
        return thread

    def cancel(self):
        self.is_cancelled = True
