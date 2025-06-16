# CleanMedia/gui/launcher_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import yaml
import json
import os

# Define file paths relative to the project root
CONFIG_DIR = 'config'
FILTERS_PATH = os.path.join(CONFIG_DIR, 'filters.json')
SETTINGS_PATH = os.path.join(CONFIG_DIR, 'settings.yaml')

# Placeholder function to simulate loading settings
def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {}

# Placeholder function to simulate loading filters
def load_filters():
    if os.path.exists(FILTERS_PATH):
        with open(FILTERS_PATH, 'r') as f:
            return json.load(f)
    return {}

class CleanMediaGUI:
    def __init__(self, master):
        self.master = master
        master.title("CleanMedia - Content Filter")
        master.geometry("600x400") # Set initial window size
        master.resizable(False, False) # Prevent resizing

        self.settings = load_settings()
        self.filters = load_filters()

        self.create_widgets()
        self.load_initial_values()

    def create_widgets(self):
        # Frame for input/output paths
        path_frame = tk.LabelFrame(self.master, text="Media Paths", padx=10, pady=10, relief="groove")
        path_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(path_frame, text="Input Video/Subtitle:").grid(row=0, column=0, sticky="w", pady=5)
        self.input_path_entry = tk.Entry(path_frame, width=50)
        self.input_path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(path_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(path_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_path_entry = tk.Entry(path_frame, width=50)
        self.output_path_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(path_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # Frame for filter settings
        filter_frame = tk.LabelFrame(self.master, text="Content Filters", padx=10, pady=10, relief="groove")
        filter_frame.pack(padx=20, pady=10, fill="x")

        self.profanity_var = tk.BooleanVar()
        self.nudity_var = tk.BooleanVar()
        self.violence_var = tk.BooleanVar()

        tk.Checkbutton(filter_frame, text="Enable Profanity Filter", variable=self.profanity_var).grid(row=0, column=0, sticky="w", pady=2)
        tk.Checkbutton(filter_frame, text="Enable Nudity Filter", variable=self.nudity_var).grid(row=1, column=0, sticky="w", pady=2)
        tk.Checkbutton(filter_frame, text="Enable Violence Filter", variable=self.violence_var).grid(row=2, column=0, sticky="w", pady=2)

        # Process Button
        process_button = tk.Button(self.master, text="Process Media", command=self.process_media,
                                    bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
        process_button.pack(pady=20, ipadx=20, ipady=10)

    def load_initial_values(self):
        # Load paths from settings
        self.input_path_entry.insert(0, self.settings.get('default_input_directory', ''))
        self.output_path_entry.insert(0, self.settings.get('default_output_directory', ''))

        # Load filter states
        self.profanity_var.set(self.filters.get('profanity', {}).get('enabled', False))
        self.nudity_var.set(self.filters.get('nudity', {}).get('enabled', False))
        self.violence_var.set(self.filters.get('violence', {}).get('enabled', False))

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Video or Subtitle File",
            filetypes=[("Media Files", "*.mp4 *.avi *.mkv *.srt"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_path_entry.delete(0, tk.END)
            self.input_path_entry.insert(0, file_path)

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, dir_path)

    def process_media(self):
        input_file = self.input_path_entry.get()
        output_dir = self.output_path_entry.get()

        if not input_file or not output_dir:
            messagebox.showerror("Error", "Please select both input file and output directory.")
            return

        # Update filter settings based on current GUI state
        self.filters['profanity']['enabled'] = self.profanity_var.get()
        self.filters['nudity']['enabled'] = self.nudity_var.get()
        self.filters['violence']['enabled'] = self.violence_var.get()

        # Save updated filters (optional, but good for persistence)
        try:
            with open(FILTERS_PATH, 'w') as f:
                json.dump(self.filters, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not save filter settings: {e}")

        messagebox.showinfo("Processing",
                            f"Processing '{os.path.basename(input_file)}'...\n"
                            f"Filters enabled: Profanity={self.profanity_var.get()}, "
                            f"Nudity={self.nudity_var.get()}, Violence={self.violence_var.get()}\n"
                            "This is a placeholder action. Real processing would happen now.")
        # Here you would call your backend processing modules:
        # e.g., from modules.metadata_builder import build_metadata
        # build_metadata(input_file, output_dir, self.filters)

def launch_tkinter_gui():
    root = tk.Tk()
    app = CleanMediaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # Ensure config directory exists
    os.makedirs(CONFIG_DIR, exist_ok=True)
    # Create dummy filter and settings files if they don't exist
    if not os.path.exists(FILTERS_PATH):
        with open(FILTERS_PATH, 'w') as f:
            json.dump({
              "profanity": {"enabled": True, "word_list": [], "replace_with": ""},
              "nudity": {"enabled": False, "detection_threshold": 0.0},
              "violence": {"enabled": False, "detection_threshold": 0.0}
            }, f, indent=2)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'w') as f:
            yaml.dump({
              "default_input_directory": "",
              "default_output_directory": "",
              "preferred_player": "vlc",
              "auto_load_filters": True,
              "verbose_logging": False,
              "gui_theme": "light",
              "max_recent_files": 5,
              "playback_speed": 1.0,
              "subtitle_encoding": "utf-8"
            }, f, indent=2)

    launch_tkinter_gui()
