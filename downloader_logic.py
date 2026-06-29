import yt_dlp
import threading
import os
import logging
import glob

logger = logging.getLogger(__name__)

class DownloadTask:
    """Represents a single download operation to ensure thread-safety."""
    def __init__(self, url, format_id, download_path, download_mode, progress_callback, finished_callback):
        self.url = url
        self.format_id = format_id
        self.download_path = download_path
        self.download_mode = download_mode
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.is_cancelled = False
        self.current_files = []

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if d['status'] == 'downloading':
            filename = d.get('filename')
            if filename and filename not in self.current_files:
                self.current_files.append(filename)

            if self.progress_callback:
                p = d.get('_percent_str', '0%').replace('%','').strip()
                try:
                    percent = float(p)
                except:
                    percent = 0.0
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                self.progress_callback(percent, speed, eta, d.get('filename'))
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100.0, "Fini", "0s", d.get('filename'))

    def run(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        ydl_opts = {
            'format': self.format_id if self.format_id else 'best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'noplaylist': True if self.download_mode == "Single" else False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            if self.finished_callback:
                self.finished_callback(True, "Téléchargement Terminé", self.current_files)
        except Exception as e:
            logger.error(f"Download error: {e}")
            self.cleanup_incomplete_files()
            if self.finished_callback:
                if "cancelled" in str(e).lower():
                     return
                self.finished_callback(False, str(e), self.current_files)

    def cancel(self):
        self.is_cancelled = True

    def cleanup_incomplete_files(self):
        for f in self.current_files:
            for ext in ['.part', '.ytdl', '.f*']:
                for partial in glob.glob(f + ext):
                    try:
                        os.remove(partial)
                    except: pass
            if os.path.exists(f):
                try:
                    os.remove(f)
                except: pass

class DownloaderLogic:
    def __init__(self, progress_callback=None, finished_callback=None):
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.active_tasks = {} # filename -> DownloadTask

    def get_info(self, url, download_mode="Single"):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True if download_mode == "Single" else False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'formats' in info:
                    info['formats'] = self._filter_formats(info['formats'])
                return info
        except Exception as e:
            logger.error(f"Error fetching info: {e}")
            return None

    def _filter_formats(self, formats):
        filtered = []
        seen = set()
        for f in formats:
            res = f.get('resolution') or f"{f.get('height','?')}p"
            ext = f.get('ext')
            if not f.get('height') and not f.get('format_note') == 'audio only':
                continue
            label = f"{res} - {ext}"
            if label not in seen:
                filtered.append(f)
                seen.add(label)
        filtered.sort(key=lambda x: x.get('height') or 0, reverse=True)
        return filtered

    def download(self, url, format_id, download_path, download_mode="Single"):
        task = DownloadTask(url, format_id, download_path, download_mode,
                            self.progress_callback, self._task_finished_wrapper)

        # We don't have the filename yet, so we'll need to update active_tasks in progress_hook or here
        # For simplicity in this structure, we'll store it by URL for now or a temp ID
        task_id = url + str(threading.get_ident())
        self.active_tasks[task_id] = task

        thread = threading.Thread(target=task.run, daemon=True)
        thread.start()
        return task_id

    def _task_finished_wrapper(self, success, msg, files):
        # Cleanup active tasks
        # This is a bit complex without a solid task_id -> files mapping
        if self.finished_callback:
            self.finished_callback(success, msg, files)

    def cancel_task(self, task_id):
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]
