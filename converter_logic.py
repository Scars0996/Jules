import subprocess
import os
import threading
import logging

logger = logging.getLogger(__name__)

class ConversionTask:
    def __init__(self, input_file, output_format, output_dir, finished_callback):
        self.input_file = input_file
        self.output_format = output_format
        self.output_dir = output_dir
        self.finished_callback = finished_callback
        self.process = None

    def run(self):
        try:
            filename = os.path.basename(self.input_file)
            name, _ = os.path.splitext(filename)
            output_file = os.path.join(self.output_dir, f"{name}.{self.output_format}")

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            command = ["ffmpeg", "-i", self.input_file, "-y", output_file]
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

            for line in self.process.stdout:
                logger.debug(line.strip())

            self.process.wait()

            if self.process.returncode == 0:
                if self.finished_callback:
                    self.finished_callback(True, f"RÉUSSI: Fichier converti !\nEmplacement: {output_file}")
            else:
                if self.finished_callback:
                    self.finished_callback(False, f"ÉCHEC: FFmpeg a quitté avec le code {self.process.returncode}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            if self.finished_callback:
                self.finished_callback(False, f"ERREUR SYSTÈME: {str(e)}")

    def cancel(self):
        if self.process:
            try:
                self.process.terminate()
            except: pass

class ConverterLogic:
    def __init__(self, progress_callback=None, finished_callback=None):
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.active_tasks = {}

    def is_ffmpeg_available(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def convert(self, input_file, output_format, output_dir):
        if not self.is_ffmpeg_available():
             if self.finished_callback:
                self.finished_callback(False, "FFmpeg non trouvé. Veuillez l'installer.")
             return

        task = ConversionTask(input_file, output_format, output_dir, self.finished_callback)
        self.active_tasks[input_file] = task
        thread = threading.Thread(target=task.run, daemon=True)
        thread.start()
        return thread

    def cancel(self, input_file):
        if input_file in self.active_tasks:
            self.active_tasks[input_file].cancel()
            del self.active_tasks[input_file]
