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
        self.root.title("Téléchargeur & Convertisseur Accessible")
        self.config = load_config()
        self.downloader = DownloaderLogic(self.safe_update_progress, self.safe_download_finished)
        self.converter = ConverterLogic(None, self.safe_conversion_finished)

        self.active_downloads = {} # task_id or filename -> UI elements

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

        self.font_main = (theme["font_family"], base_size)
        self.font_large = (theme["font_family"], large_size, "bold")

        self.root.configure(bg=theme["bg"])

        self.style.configure("TNotebook", background=theme["bg"])
        self.style.configure("TNotebook.Tab", font=self.font_large, padding=[20, 10])
        self.style.configure("TLabelframe", background=theme["bg"], foreground=theme["fg"])
        self.style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"], font=self.font_large)
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["fg"], font=self.font_main)
        self.style.configure("TButton", font=self.font_main, padding=10)

        self.btn_coller.configure(bg=theme["paste_btn"], fg="white", font=self.font_large)
        self.btn_supprimer.configure(bg=theme["delete_btn"], fg="white", font=self.font_large)
        self.btn_telecharger.configure(bg=theme["download_btn"], fg="white", font=self.font_large)
        self.conv_btn_lancer.configure(bg=theme["download_btn"], fg="white", font=self.font_large)

        self.update_widget_colors(self.root, theme, self.font_main, self.font_large)

    def update_widget_colors(self, container, theme, font_main, font_large):
        for widget in container.winfo_children():
            try:
                if isinstance(widget, (tk.Entry, tk.Listbox, tk.Text)):
                    widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                     insertbackground=theme["fg"], font=font_main)
                elif isinstance(widget, tk.Button):
                    if widget not in [self.btn_coller, self.btn_supprimer, self.btn_telecharger, self.conv_btn_lancer]:
                        widget.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=font_main)
                elif isinstance(widget, (tk.Label, tk.Frame)):
                    widget.configure(bg=theme["bg"])

                if hasattr(widget, "winfo_children"):
                    self.update_widget_colors(widget, theme, font_main, font_large)
            except:
                pass

    def create_widgets(self):
        # 3-Button Header
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.btn_coller = tk.Button(self.header_frame, text="COLLER LE LIEN", command=self.paste_link)
        self.btn_coller.pack(side="left", expand=True, fill="both", padx=5)

        self.btn_supprimer = tk.Button(self.header_frame, text="SUPPRIMER", command=self.delete_input)
        self.btn_supprimer.pack(side="left", expand=True, fill="both", padx=5)

        self.btn_telecharger = tk.Button(self.header_frame, text="TÉLÉCHARGER", command=self.start_download)
        self.btn_telecharger.pack(side="left", expand=True, fill="both", padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_downloader = ttk.Frame(self.notebook)
        self.tab_downloading = ttk.Frame(self.notebook)
        self.tab_converter = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_downloader, text="  TÉLÉCHARGEMENT  ")
        self.notebook.add(self.tab_downloading, text="  EN COURS  ")
        self.notebook.add(self.tab_converter, text="  CONVERTISSEUR  ")
        self.notebook.add(self.tab_settings, text="  PARAMÈTRES  ")

        self.setup_downloader_tab()
        self.setup_downloading_tab()
        self.setup_converter_tab()
        self.setup_settings_tab()

    def setup_downloader_tab(self):
        self.tab_downloader.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_downloader, text="Configuration")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="URL de la vidéo:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self.on_url_change)
        self.url_entry = tk.Entry(frame, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        self.mode_frame = tk.Frame(frame)
        self.mode_frame.grid(row=2, column=0, pady=10)
        self.mode_var = tk.StringVar(value=self.config["download_mode"])
        tk.Radiobutton(self.mode_frame, text="Vidéo Seule", variable=self.mode_var, value="Single", command=self.save_mode).pack(side="left", padx=20)
        tk.Radiobutton(self.mode_frame, text="Playlist", variable=self.mode_var, value="Playlist", command=self.save_mode).pack(side="left", padx=20)

        self.btn_fetch = tk.Button(frame, text="VÉRIFIER LE LIEN / RÉCUPÉRER QUALITÉS", command=self.fetch_formats)
        self.btn_fetch.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        self.quality_frame = ttk.LabelFrame(frame, text="Choix de Qualité (Mémorisé)")
        self.quality_frame.grid(row=4, column=0, pady=10, padx=10, sticky="nsew")
        self.quality_frame.columnconfigure((0,1,2), weight=1)

    def setup_downloading_tab(self):
        self.tab_downloading.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.tab_downloading)
        self.scrollbar = ttk.Scrollbar(self.tab_downloading, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

    def setup_converter_tab(self):
        self.tab_converter.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_converter, text="Convertir un fichier local")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        self.selected_file_label = ttk.Label(frame, text="Aucun fichier sélectionné", wraplength=500)
        self.selected_file_label.grid(row=0, column=0, pady=20)

        tk.Button(frame, text="CHOISIR UN FICHIER", command=self.select_file_for_conversion).grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        ttk.Label(frame, text="Format de sortie:").grid(row=2, column=0, pady=(20, 5))
        self.conv_format_var = tk.StringVar(value=self.config["saved_format"])
        formats = ["mp3", "mp4", "mkv", "wav", "flac"]
        self.conv_format_menu = ttk.Combobox(frame, textvariable=self.conv_format_var, values=formats, state="readonly")
        self.conv_format_menu.grid(row=3, column=0, pady=5)
        self.conv_format_menu.bind("<<ComboboxSelected>>", self.save_conv_format)

        self.conv_btn_lancer = tk.Button(frame, text="LANCER LA CONVERSION", command=self.start_conversion)
        self.conv_btn_lancer.grid(row=4, column=0, pady=30, padx=20, sticky="ew")

    def setup_settings_tab(self):
        self.tab_settings.columnconfigure(0, weight=1)
        frame = ttk.LabelFrame(self.tab_settings, text="Préférences")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        self.auto_dl_var = tk.BooleanVar(value=self.config["auto_download"])
        tk.Checkbutton(frame, text="Téléchargement Auto (au collage)", variable=self.auto_dl_var, command=self.save_settings_ui).grid(row=0, column=0, pady=10, sticky="w", padx=10)

        ttk.Label(frame, text="Dossier Téléchargement:").grid(row=1, column=0, pady=(10, 2), padx=10, sticky="w")
        self.dl_path_var = tk.StringVar(value=self.config["download_path"])
        tk.Entry(frame, textvariable=self.dl_path_var).grid(row=2, column=0, padx=10, sticky="ew")
        tk.Button(frame, text="Changer", command=lambda: self.browse_path("download_path")).grid(row=2, column=1, padx=10)

        ttk.Label(frame, text="Thème:").grid(row=3, column=0, pady=(20, 5), padx=10, sticky="w")
        self.theme_var = tk.StringVar(value=self.config["theme"])
        themes = ["Contraste Élevé", "Texte Large Clair", "Spécial Cataracte"]
        cb_theme = ttk.Combobox(frame, textvariable=self.theme_var, values=themes, state="readonly")
        cb_theme.grid(row=4, column=0, padx=10, sticky="ew")
        cb_theme.bind("<<ComboboxSelected>>", self.save_settings_ui)

        ttk.Label(frame, text="Taille Texte:").grid(row=5, column=0, pady=(20, 5), padx=10, sticky="w")
        self.font_scale_var = tk.DoubleVar(value=self.config["font_scale"])
        tk.Scale(frame, from_=1.0, to=3.0, resolution=0.1, orient="horizontal", variable=self.font_scale_var, command=lambda x: self.save_settings_ui()).grid(row=6, column=0, padx=10, sticky="ew")

    # Handlers
    def paste_link(self):
        try:
            self.url_var.set(self.root.clipboard_get())
        except: pass

    def delete_input(self):
        self.url_var.set("")
        for w in self.quality_frame.winfo_children(): w.destroy()

    def on_url_change(self, *args):
        if self.auto_dl_var.get() and self.url_var.get().startswith("http"):
            self.fetch_formats()

    def save_mode(self):
        self.config["download_mode"] = self.mode_var.get()
        save_config(self.config)

    def save_conv_format(self, *args):
        self.config["saved_format"] = self.conv_format_var.get()
        save_config(self.config)

    def fetch_formats(self):
        url = self.url_var.get().strip()
        if not url: return
        self.btn_fetch.config(text="RECHERCHE EN COURS...", state="disabled")
        threading.Thread(target=self._async_fetch, args=(url,), daemon=True).start()

    def _async_fetch(self, url):
        info = self.downloader.get_info(url, self.mode_var.get())
        self.root.after(0, self.finalize_fetch, info)

    def finalize_fetch(self, info):
        self.btn_fetch.config(text="VÉRIFIER LE LIEN / RÉCUPÉRER QUALITÉS", state="normal")
        if info:
            self.populate_formats(info)
            if self.auto_dl_var.get():
                self.start_download()
        else: messagebox.showerror("Erreur", "Lien invalide ou erreur réseau")

    def populate_formats(self, info):
        for w in self.quality_frame.winfo_children(): w.destroy()
        formats = info.get('formats', [])

        # Sort and filter for better buttons
        # We want to show a few best options
        resolutions = {}
        for f in formats:
            h = f.get('height')
            if h and h not in resolutions:
                resolutions[h] = f

        sorted_heights = sorted(resolutions.keys(), reverse=True)

        row, col = 0, 0
        theme_colors = get_theme_colors(self.config["theme"])

        for h in sorted_heights[:12]: # Show up to 12 buttons
            f = resolutions[h]
            res = f.get('resolution') or f"{h}p"
            ext = f.get('ext')
            fid = f.get('format_id')

            # Use large buttons for better visibility
            btn = tk.Button(self.quality_frame, text=f"{res}\n{ext.upper()}",
                            command=lambda q=fid: self.select_quality(q),
                            width=10, height=2)
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

            if fid == self.config["saved_quality"]:
                btn.configure(bg=theme_colors["accent"], fg="black")
            else:
                btn.configure(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])

            col += 1
            if col > 2:
                col = 0
                row += 1

    def select_quality(self, quality_id):
        self.config["saved_quality"] = quality_id
        save_config(self.config)
        # Redraw to show selection
        url = self.url_var.get().strip()
        if url: self.fetch_formats()

    def start_download(self):
        url = self.url_var.get().strip()
        if not url: return
        self.notebook.select(self.tab_downloading)
        task_id = self.downloader.download(url, self.config["saved_quality"], self.config["download_path"], self.mode_var.get())
        # Associate task_id with something so we can cancel it
        # We'll use filename when it arrives in progress update

    def safe_update_progress(self, percent, speed, eta, filename):
        self.root.after(0, self.update_progress_ui, percent, speed, eta, filename)

    def update_progress_ui(self, percent, speed, eta, filename):
        if filename not in self.active_downloads:
            frame = ttk.Frame(self.scroll_frame)
            frame.pack(fill="x", pady=15, padx=10)

            lbl = ttk.Label(frame, text=os.path.basename(filename), wraplength=600, font=self.font_large)
            lbl.pack(anchor="w")

            pbar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=500)
            pbar.pack(fill="x", pady=10)

            info_lbl = ttk.Label(frame, text="", font=self.font_main)
            info_lbl.pack(anchor="w")

            btn_frame = tk.Frame(frame, bg=frame.cget("background"))
            btn_frame.pack(anchor="e", pady=5)

            btn_stop = tk.Button(btn_frame, text="ARRÊTER (NETTOYAGE DISQUE)", bg="#DC3545", fg="white",
                                 command=lambda f=filename: self.stop_specific_download(f))
            btn_stop.pack(side="right", padx=5)

            btn_remove = tk.Button(btn_frame, text="RETIRER DE LA LISTE", bg="#6c757d", fg="white",
                                   command=lambda f=filename: self.remove_from_list_only(f))
            btn_remove.pack(side="right", padx=5)

            self.active_downloads[filename] = {"frame": frame, "pbar": pbar, "info": info_lbl, "done": False}

        items = self.active_downloads[filename]
        items["pbar"]["value"] = percent
        items["info"].config(text=f"{percent}% - Vitesse: {speed} - Temps restant: {eta}")
        if percent >= 100:
            items["done"] = True
            items["info"].config(text="TERMINÉ")

    def stop_specific_download(self, filename):
        # We need to find the task_id for this filename.
        # For now, let's just trigger a general cancel or refine the task management.
        # Given the logic refactor, we should find the correct task.
        for tid, task in self.downloader.active_tasks.items():
            if filename in task.current_files:
                self.downloader.cancel_task(tid)
                break

        if filename in self.active_downloads:
            self.active_downloads[filename]["frame"].destroy()
            del self.active_downloads[filename]
        messagebox.showinfo("Information", f"Téléchargement arrêté : {os.path.basename(filename)}")

    def remove_from_list_only(self, filename):
        if filename in self.active_downloads:
            self.active_downloads[filename]["frame"].destroy()
            del self.active_downloads[filename]

    def safe_download_finished(self, success, msg, files):
        self.root.after(0, self.download_finished_ui, success, msg, files)

    def download_finished_ui(self, success, msg, files):
        for f in files:
            if f in self.active_downloads:
                self.active_downloads[f]["frame"].destroy()
                del self.active_downloads[f]
        if success: messagebox.showinfo("Succès", "Téléchargement terminé !")
        else: messagebox.showerror("Erreur", msg)

    def select_file_for_conversion(self):
        f = filedialog.askopenfilename()
        if f: self.selected_file_label.config(text=os.path.basename(f)); self.selected_file_path = f

    def start_conversion(self):
        if hasattr(self, 'selected_file_path'):
            self.converter.convert(self.selected_file_path, self.config["saved_format"], self.config["converter_path"])

    def safe_conversion_finished(self, success, msg):
        self.root.after(0, lambda: messagebox.showinfo("Conversion", msg) if success else messagebox.showerror("Erreur", msg))

    def browse_path(self, key):
        p = filedialog.askdirectory()
        if p: self.dl_path_var.set(p) if key=="download_path" else None; self.save_settings_ui()

    def save_settings_ui(self, *args):
        self.config.update({"download_path": self.dl_path_var.get(), "theme": self.theme_var.get(), "font_scale": self.font_scale_var.get(), "auto_download": self.auto_dl_var.get()})
        save_config(self.config); self.apply_theme()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x900")
    app = AppGUI(root)
    root.mainloop()
