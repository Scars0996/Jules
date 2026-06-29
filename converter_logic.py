import subprocess
import os
import threading
import logging

logger = logging.getLogger(__name__)

class ConverterLogic:
    def __init__(self, progress_callback=None, finished_callback=None):
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.process = None

    def is_ffmpeg_available(self):
        try:
            # On Windows, we might need to check ffmpeg.exe
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def convert(self, input_file, output_format, output_dir):
        if not self.is_ffmpeg_available():
             if self.finished_callback:
                self.finished_callback(False, "CRITICAL ERROR: FFmpeg not found on this system.\n\nPlease install FFmpeg and ensure it's in your Windows System PATH to use the Converter and high-quality YouTube downloads.")
             return

        def run():
            try:
                filename = os.path.basename(input_file)
                name, _ = os.path.splitext(filename)
                output_file = os.path.join(output_dir, f"{name}.{output_format}")

                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                command = ["ffmpeg", "-i", input_file, "-y", output_file]

                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

                # Simple loop to read output and prevent hanging
                for line in self.process.stdout:
                    logger.debug(line.strip())

                self.process.wait()

                if self.process.returncode == 0:
                    if self.finished_callback:
                        self.finished_callback(True, f"SUCCESS: File converted successfully!\nLocation: {output_file}")
                else:
                    if self.finished_callback:
                        self.finished_callback(False, f"CONVERSION FAILED: FFmpeg exited with error code {self.process.returncode}. The file might be corrupted or in an unsupported format.")
            except Exception as e:
                logger.error(f"Conversion error: {e}")
                if self.finished_callback:
                    self.finished_callback(False, f"SYSTEM ERROR: {str(e)}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def cancel(self):
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
