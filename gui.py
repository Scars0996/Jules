import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import load_config, save_config, get_theme_colors
from downloader_logic import DownloaderLogic
from converter_logic import ConverterLogic
from updater import check_for_ytdlp_updates
import threading
import os

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Accessible YT Downloader & Converter")
        self.config = load_config()
        self.downloader = DownloaderLogic(self.update_progress, self.download_finished)
        self.converter = ConverterLogic(None, self.conversion_finished)

        self.setup_styles()
        self.create_widgets()
        self.apply_theme()

        if self.config.get("auto_update_ytdlp"):
            threading.Thread(target=check_for_ytdlp_updates).start()

    def setup_styles(self):
        self.style = ttk.Style()
        # We will dynamically update styles in apply_theme

    def apply_theme(self):
        theme = get_theme_colors(self.config["theme"])
        scale = self.config["font_scale"]
        base_size = int(12 * scale)
        large_size = int(16 * scale)

        font_main = (theme["font_family"], base_size)
        font_large = (theme["font_family"], large_size, "bold")

        self.root.configure(bg=theme["bg"])

        # Configure TLabelframe
        self.style.configure("TLabelframe", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"], font=font_large)

        # Configure TButton
        self.style.configure("TButton", font=font_main)

        # Configure TNotebook
        self.style.configure("TNotebook", background=theme["bg"])
        self.style.configure("TNotebook.Tab", font=font_large, padding=[10, 5])

        # Configure TLabel
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"], font=font_main)

        # Recursively update all widgets that don't use ttk styles or need direct config
        self.update_widget_colors(self.root, theme, font_main, font_large)

    def update_widget_colors(self, container, theme, font_main, font_large):
        for widget in container.winfo_children():
            try:
                if isinstance(widget, (tk.Entry, tk.Listbox, tk.Text)):
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"], insertbackground=theme["fg"], font=font_main)
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=font_main)
                elif isinstance(widget, (tk.Label, tk.Frame)):
                    widget.configure(bg=theme["bg"])

                if hasattr(widget, "winfo_children"):
                    self.update_widget_colors(widget, theme, font_main, font_large)
            except:
                pass

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_downloader = ttk.Frame(self.notebook)
        self.tab_downloading = ttk.Frame(self.notebook)
        self.tab_converter = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_downloader, text=" Downloader ")
        self.notebook.add(self.tab_downloading, text=" Downloading ")
        self.notebook.add(self.tab_converter, text=" Converter ")
        self.notebook.add(self.tab_settings, text=" Settings ")

        self.setup_downloader_tab()
        self.setup_downloading_tab()
        self.setup_converter_tab()
        self.setup_settings_tab()

    def setup_downloader_tab(self):
        frame = ttk.LabelFrame(self.tab_downloader, text="Download New Video")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="YouTube URL:").pack(pady=5)
        self.url_entry = tk.Entry(frame, width=50)
        self.url_entry.pack(pady=5, padx=10, fill="x")

        btn_fetch = tk.Button(frame, text="Fetch Formats", command=self.fetch_formats)
        btn_fetch.pack(pady=10)

        ttk.Label(frame, text="Select Quality:").pack(pady=5)
        self.format_listbox = tk.Listbox(frame, height=10)
        self.format_listbox.pack(pady=5, padx=10, fill="both", expand=True)

        self.btn_download = tk.Button(frame, text="START DOWNLOAD", command=self.start_download)
        self.btn_download.pack(pady=20)

    def setup_downloading_tab(self):
        frame = ttk.LabelFrame(self.tab_downloading, text="Current Progress")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.progress_label = ttk.Label(frame, text="No active download")
        self.progress_label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=20, padx=20, fill="x")

        self.speed_label = ttk.Label(frame, text="Speed: -")
        self.speed_label.pack(pady=5)

        self.eta_label = ttk.Label(frame, text="ETA: -")
        self.eta_label.pack(pady=5)

        tk.Button(frame, text="CANCEL", command=self.cancel_download).pack(pady=20)

    def setup_converter_tab(self):
        frame = ttk.LabelFrame(self.tab_converter, text="Convert Local File")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.selected_file_label = ttk.Label(frame, text="No file selected")
        self.selected_file_label.pack(pady=10)

        tk.Button(frame, text="Select File", command=self.select_file_for_conversion).pack(pady=5)

        ttk.Label(frame, text="Output Format:").pack(pady=10)
        self.output_format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "mp4", "mkv", "wav"]
        format_menu = ttk.Combobox(frame, textvariable=self.output_format_var, values=formats, state="readonly")
        format_menu.pack(pady=5)

        tk.Button(frame, text="CONVERT NOW", command=self.start_conversion).pack(pady=20)

    def setup_settings_tab(self):
        frame = ttk.LabelFrame(self.tab_settings, text="Application Settings")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Download Path
        ttk.Label(frame, text="Default Download Path:").pack(pady=5)
        self.dl_path_var = tk.StringVar(value=self.config["download_path"])
        entry_dl = tk.Entry(frame, textvariable=self.dl_path_var)
        entry_dl.pack(fill="x", padx=10)
        tk.Button(frame, text="Browse", command=lambda: self.browse_path("download_path")).pack(pady=2)

        # Converter Path
        ttk.Label(frame, text="Default Converter Path:").pack(pady=5)
        self.conv_path_var = tk.StringVar(value=self.config["converter_path"])
        entry_conv = tk.Entry(frame, textvariable=self.conv_path_var)
        entry_conv.pack(fill="x", padx=10)
        tk.Button(frame, text="Browse", command=lambda: self.browse_path("converter_path")).pack(pady=2)

        # Theme
        ttk.Label(frame, text="Accessibility Theme:").pack(pady=10)
        self.theme_var = tk.StringVar(value=self.config["theme"])
        themes = ["High Contrast", "Large Text Light", "Cataract Friendly"]
        theme_menu = ttk.Combobox(frame, textvariable=self.theme_var, values=themes, state="readonly")
        theme_menu.pack(pady=5)

        # Font Scale
        ttk.Label(frame, text="Font Scale (1.0 - 3.0):").pack(pady=5)
        self.font_scale_var = tk.DoubleVar(value=self.config["font_scale"])
        scale_slider = tk.Scale(frame, from_=1.0, to=3.0, resolution=0.1, orient="horizontal", variable=self.font_scale_var)
        scale_slider.pack(fill="x", padx=10)

        tk.Button(frame, text="SAVE SETTINGS", command=self.save_settings_ui).pack(pady=20)

    # Logic Handlers
    def fetch_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        def run():
            info = self.downloader.get_info(url)
            if info:
                self.root.after(0, lambda: self.populate_formats(info))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to fetch info"))

        threading.Thread(target=run).start()

    def populate_formats(self, info):
        self.format_listbox.delete(0, tk.END)
        self.formats_data = info.get('formats', [])
        for f in self.formats_data:
            desc = f"{f.get('format_note', 'N/A')} - {f.get('ext')} - {f.get('resolution', 'N/A')}"
            self.format_listbox.insert(tk.END, desc)

    def start_download(self):
        url = self.url_entry.get()
        selection = self.format_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a quality first")
            return

        format_id = self.formats_data[selection[0]]['format_id']
        self.notebook.select(self.tab_downloading)
        self.downloader.download(url, format_id, self.config["download_path"])

    def update_progress(self, percent, speed, eta):
        self.progress_bar['value'] = percent
        self.progress_label.config(text=f"Downloading... {percent}%")
        self.speed_label.config(text=f"Speed: {speed}")
        self.eta_label.config(text=f"ETA: {eta}")

    def download_finished(self, success, msg):
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready")

    def cancel_download(self):
        self.downloader.cancel()
        messagebox.showinfo("Cancelled", "Download cancellation requested")

    def select_file_for_conversion(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file_path = file_path
            self.selected_file_label.config(text=os.path.basename(file_path))

    def start_conversion(self):
        if not hasattr(self, 'selected_file_path'):
            messagebox.showwarning("Warning", "Select a file first")
            return
        self.converter.convert(self.selected_file_path, self.output_format_var.get(), self.config["converter_path"])

    def conversion_finished(self, success, msg):
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def browse_path(self, key):
        path = filedialog.askdirectory()
        if path:
            if key == "download_path":
                self.dl_path_var.set(path)
            elif key == "converter_path":
                self.conv_path_var.set(path)

    def save_settings_ui(self):
        self.config["download_path"] = self.dl_path_var.get()
        self.config["converter_path"] = self.conv_path_var.get()
        self.config["theme"] = self.theme_var.get()
        self.config["font_scale"] = self.font_scale_var.get()
        save_config(self.config)
        self.apply_theme()
        messagebox.showinfo("Saved", "Settings saved and applied.")

if __name__ == "__main__":
    root = tk.Tk()
    # On headless environments this will fail, but for local dev it's okay
    try:
        app = AppGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"GUI failed to start: {e}")
