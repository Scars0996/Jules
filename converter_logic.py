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
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def convert(self, input_file, output_format, output_dir):
        if not self.is_ffmpeg_available():
             if self.finished_callback:
                self.finished_callback(False, "FFmpeg not found. Please install FFmpeg and add it to your PATH.")
             return

        def run():
            filename = os.path.basename(input_file)
            name, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}.{output_format}")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Basic ffmpeg command
            # For progress, it's more complex with ffmpeg, but we can do a simple check
            command = ["ffmpeg", "-i", input_file, "-y", output_file]

            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

                # Ffmpeg sends progress to stderr by default, but we redirected it to stdout
                for line in self.process.stdout:
                    # Simple progress simulation or parsing could go here
                    # For now, just logging
                    logger.debug(line.strip())

                self.process.wait()

                if self.process.returncode == 0:
                    if self.finished_callback:
                        self.finished_callback(True, f"Converted to {output_file}")
                else:
                    if self.finished_callback:
                        self.finished_callback(False, "Conversion failed. Is ffmpeg installed?")
            except Exception as e:
                logger.error(f"Conversion error: {e}")
                if self.finished_callback:
                    self.finished_callback(False, str(e))

        thread = threading.Thread(target=run)
        thread.start()
        return thread

    def cancel(self):
        if self.process:
            self.process.terminate()
