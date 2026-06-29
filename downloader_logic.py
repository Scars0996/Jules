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
                # Group and filter formats for better readability
                if 'formats' in info:
                    info['formats'] = self._filter_formats(info['formats'])
                return info
        except Exception as e:
            logger.error(f"Error fetching info: {e}")
            return None

    def _filter_formats(self, formats):
        """Filters and sorts formats to show best options for each resolution."""
        filtered = []
        seen = set()
        # Preferred order: mp4, mkv, then others
        # We want to show a clear list of resolutions

        # First, only take formats with both audio and video or common formats
        for f in formats:
            res = f.get('resolution') or f"{f.get('height','?')}p"
            ext = f.get('ext')
            # Skip formats without resolution (audio only etc handled differently if needed)
            if not f.get('height') and not f.get('format_note') == 'audio only':
                continue

            label = f"{res} - {ext}"
            if label not in seen:
                filtered.append(f)
                seen.add(label)

        # Sort by height descending
        filtered.sort(key=lambda x: x.get('height') or 0, reverse=True)
        return filtered

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if self.progress_callback:
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%').replace('%','').strip()
                try:
                    percent = float(p)
                except:
                    percent = 0.0
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                self.progress_callback(percent, speed, eta)
            elif d['status'] == 'finished':
                self.progress_callback(100.0, "Done", "0s")

    def download(self, url, format_id, download_path):
        def run():
            if not os.path.exists(download_path):
                os.makedirs(download_path)

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
                    # If it was cancelled, don't show error message as error
                    if "cancelled" in str(e).lower():
                         return
                    self.finished_callback(False, str(e))

        self.is_cancelled = False
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def cancel(self):
        self.is_cancelled = True
