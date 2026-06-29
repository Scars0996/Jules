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
        self.downloader = DownloaderLogic(self.safe_update_progress, self.safe_download_finished)
        self.converter = ConverterLogic(None, self.safe_conversion_finished)

        self.setup_styles()
        self.create_widgets()
        self.apply_theme()

        if self.config.get("auto_update_ytdlp"):
            threading.Thread(target=check_for_ytdlp_updates, daemon=True).start()

    def setup_styles(self):
        self.style = ttk.Style()

    def apply_theme(self):
        theme = get_theme_colors(self.config["theme"])
        scale = self.config["font_scale"]
        base_size = int(14 * scale)
        large_size = int(18 * scale)

        font_main = (theme["font_family"], base_size)
        font_large = (theme["font_family"], large_size, "bold")

        self.root.configure(bg=theme["bg"])

        # Style configurations
        self.style.configure("TNotebook", background=theme["bg"])
        self.style.configure("TNotebook.Tab", font=font_large, padding=[20, 10])
        self.style.configure("TLabelframe", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"], font=font_large)
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"], font=font_main)
        self.style.configure("TButton", font=font_main, padding=10)

        self.update_widget_colors(self.root, theme, font_main, font_large)

    def update_widget_colors(self, container, theme, font_main, font_large):
        for widget in container.winfo_children():
            try:
                if isinstance(widget, (tk.Entry, tk.Listbox, tk.Text)):
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                     insertbackground=theme["fg"], font=font_main,
                                     highlightthickness=2, highlightcolor=theme["accent"])
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                     font=font_main, activebackground=theme["accent"],
                                     padx=10, pady=10)
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

        self.notebook.add(self.tab_downloader, text="  Downloader  ")
        self.notebook.add(self.tab_downloading, text="  Downloading  ")
        self.notebook.add(self.tab_converter, text="  Converter  ")
        self.notebook.add(self.tab_settings, text="  Settings  ")

        self.setup_downloader_tab()
        self.setup_downloading_tab()
        self.setup_converter_tab()
        self.setup_settings_tab()

    def setup_downloader_tab(self):
        self.tab_downloader.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.tab_downloader, text="Download New Video")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Paste YouTube URL here:").grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

        self.url_entry = tk.Entry(frame)
        self.url_entry.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        self.btn_fetch = tk.Button(frame, text="FETCH AVAILABLE QUALITIES", command=self.fetch_formats)
        self.btn_fetch.grid(row=2, column=0, pady=15, padx=10, sticky="ew")

        ttk.Label(frame, text="Select a Quality:").grid(row=3, column=0, pady=(10, 5), padx=10, sticky="w")

        self.format_listbox = tk.Listbox(frame, height=8)
        self.format_listbox.grid(row=4, column=0, pady=5, padx=10, sticky="nsew")

        self.btn_download = tk.Button(frame, text="START DOWNLOAD NOW", command=self.start_download)
        self.btn_download.grid(row=5, column=0, pady=20, padx=10, sticky="ew")

    def setup_downloading_tab(self):
        self.tab_downloading.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_downloading, text="Current Download Progress")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        self.progress_label = ttk.Label(frame, text="Ready to download")
        self.progress_label.grid(row=0, column=0, pady=20)

        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, pady=20, padx=20, sticky="ew")

        self.speed_label = ttk.Label(frame, text="Speed: -")
        self.speed_label.grid(row=2, column=0, pady=5)

        self.eta_label = ttk.Label(frame, text="Time Remaining: -")
        self.eta_label.grid(row=3, column=0, pady=5)

        self.btn_cancel = tk.Button(frame, text="CANCEL DOWNLOAD", command=self.cancel_download)
        self.btn_cancel.grid(row=4, column=0, pady=30, padx=20, sticky="ew")

    def setup_converter_tab(self):
        self.tab_converter.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_converter, text="Convert Local Media File")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        self.selected_file_label = ttk.Label(frame, text="No file selected", wraplength=500)
        self.selected_file_label.grid(row=0, column=0, pady=20)

        tk.Button(frame, text="BROWSE FOR FILE", command=self.select_file_for_conversion).grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        ttk.Label(frame, text="Choose Output Format:").grid(row=2, column=0, pady=(20, 5))
        self.output_format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "mp4", "mkv", "wav", "flac"]
        self.format_menu = ttk.Combobox(frame, textvariable=self.output_format_var, values=formats, state="readonly")
        self.format_menu.grid(row=3, column=0, pady=5, padx=20)

        tk.Button(frame, text="CONVERT FILE NOW", command=self.start_conversion).grid(row=4, column=0, pady=30, padx=20, sticky="ew")

    def setup_settings_tab(self):
        self.tab_settings.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_settings, text="Application Settings")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        # Download Path
        ttk.Label(frame, text="Default Download Folder:").grid(row=0, column=0, pady=(10, 2), padx=10, sticky="w")
        self.dl_path_var = tk.StringVar(value=self.config["download_path"])
        tk.Entry(frame, textvariable=self.dl_path_var).grid(row=1, column=0, padx=10, sticky="ew")
        tk.Button(frame, text="Browse Folder", command=lambda: self.browse_path("download_path")).grid(row=1, column=1, padx=10)

        # Converter Path
        ttk.Label(frame, text="Default Converter Folder:").grid(row=2, column=0, pady=(10, 2), padx=10, sticky="w")
        self.conv_path_var = tk.StringVar(value=self.config["converter_path"])
        tk.Entry(frame, textvariable=self.conv_path_var).grid(row=3, column=0, padx=10, sticky="ew")
        tk.Button(frame, text="Browse Folder", command=lambda: self.browse_path("converter_path")).grid(row=3, column=1, padx=10)

        # Theme
        ttk.Label(frame, text="Visual Theme (Accessibility):").grid(row=4, column=0, pady=(20, 5), padx=10, sticky="w")
        self.theme_var = tk.StringVar(value=self.config["theme"])
        themes = ["High Contrast", "Large Text Light", "Cataract Friendly"]
        ttk.Combobox(frame, textvariable=self.theme_var, values=themes, state="readonly").grid(row=5, column=0, padx=10, sticky="ew")

        # Font Scale
        ttk.Label(frame, text="Text Size Adjustment:").grid(row=6, column=0, pady=(20, 5), padx=10, sticky="w")
        self.font_scale_var = tk.DoubleVar(value=self.config["font_scale"])
        tk.Scale(frame, from_=1.0, to=3.0, resolution=0.1, orient="horizontal", variable=self.font_scale_var).grid(row=7, column=0, padx=10, sticky="ew")

        tk.Button(frame, text="SAVE AND APPLY SETTINGS", command=self.save_settings_ui).grid(row=8, column=0, columnspan=2, pady=30, padx=10, sticky="ew")

    # Thread-Safe Handlers
    def safe_update_progress(self, percent, speed, eta):
        self.root.after(0, self.update_progress, percent, speed, eta)

    def safe_download_finished(self, success, msg):
        self.root.after(0, self.download_finished, success, msg)

    def safe_conversion_finished(self, success, msg):
        self.root.after(0, self.conversion_finished, success, msg)

    # UI Logic
    def fetch_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste a YouTube URL first.")
            return

        self.btn_fetch.config(text="FETCHING... PLEASE WAIT", state="disabled")

        def run():
            info = self.downloader.get_info(url)
            self.root.after(0, self.finalize_fetch, info)

        threading.Thread(target=run, daemon=True).start()

    def finalize_fetch(self, info):
        self.btn_fetch.config(text="FETCH AVAILABLE QUALITIES", state="normal")
        if info:
            self.populate_formats(info)
        else:
            messagebox.showerror("Error", "Could not retrieve video information. Check your URL and internet connection.")

    def populate_formats(self, info):
        self.format_listbox.delete(0, tk.END)
        # We will improve filtering in downloader_logic, but here we just display what we get
        self.formats_data = info.get('formats', [])
        # Simple filtering for readable list
        seen_resolutions = set()
        self.filtered_formats = []

        for f in self.formats_data:
            res = f.get('resolution') or f"{f.get('width','?')}x{f.get('height','?')}"
            ext = f.get('ext')
            note = f.get('format_note', '')
            if res and res not in seen_resolutions:
                desc = f"{res} - {ext} ({note})"
                self.format_listbox.insert(tk.END, desc)
                self.filtered_formats.append(f)
                # seen_resolutions.add(res) # Commented out to show more options for now

    def start_download(self):
        url = self.url_entry.get().strip()
        selection = self.format_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a quality from the list first.")
            return

        format_id = self.filtered_formats[selection[0]]['format_id']
        self.notebook.select(self.tab_downloading)
        self.downloader.download(url, format_id, self.config["download_path"])

    def update_progress(self, percent, speed, eta):
        self.progress_bar['value'] = percent
        self.progress_label.config(text=f"Downloading: {percent}%")
        self.speed_label.config(text=f"Current Speed: {speed}")
        self.eta_label.config(text=f"Time Remaining: {eta}")

    def download_finished(self, success, msg):
        if success:
            messagebox.showinfo("Success", "Download completed successfully!")
        else:
            messagebox.showerror("Download Error", msg)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready to download")

    def cancel_download(self):
        self.downloader.cancel()
        messagebox.showinfo("Cancelled", "Download has been cancelled.")

    def select_file_for_conversion(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file_path = file_path
            self.selected_file_label.config(text=f"Selected: {os.path.basename(file_path)}")

    def start_conversion(self):
        if not hasattr(self, 'selected_file_path'):
            messagebox.showwarning("Warning", "Please select a file to convert.")
            return
        self.converter.convert(self.selected_file_path, self.output_format_var.get(), self.config["converter_path"])

    def conversion_finished(self, success, msg):
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Conversion Error", msg)

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
        messagebox.showinfo("Settings Saved", "Your settings have been saved and applied.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x900")
    try:
        app = AppGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"GUI failed to start: {e}")
