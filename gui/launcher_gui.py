# CleanMedia/gui/launcher_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
import threading
import time

# Import the centralized config manager
from modules.config_manager import load_settings, save_settings, load_filters, save_filters, initialize_config_files

# Placeholder for modules that will be imported dynamically
# This prevents circular imports if they also import config_manager
metadata_builder = None
player_overlay = None

class CleanMediaGUI:
    def __init__(self, master):
        self.master = master
        master.title("CleanMedia - Content Filter")
        master.geometry("800x650") # Increased window size for more controls
        master.resizable(True, True) # Allow resizing for better usability

        # Load initial settings and filters
        self.settings = load_settings()
        self.filters = load_filters()

        self.create_widgets()
        self.load_initial_values()

        # Apply GUI theme from settings
        self.apply_theme(self.settings.get('gui_theme', 'light'))

    def apply_theme(self, theme_name):
        """Applies visual theme to the GUI."""
        if theme_name == 'dark':
            bg_color = "#333333"
            fg_color = "#FFFFFF"
            label_bg = "#444444"
            entry_bg = "#555555"
            button_bg = "#666666"
            button_fg = "#FFFFFF"
            frame_bg = "#444444"
        else: # 'light' or default
            bg_color = "#F0F0F0"
            fg_color = "#000000"
            label_bg = "#E0E0E0"
            entry_bg = "#FFFFFF"
            button_bg = "#DDDDDD"
            button_fg = "#000000"
            frame_bg = "#E0E0E0"

        self.master.config(bg=bg_color)
        for widget in self.master.winfo_children():
            if isinstance(widget, (tk.LabelFrame, tk.Frame)):
                widget.config(bg=frame_bg, fg=fg_color)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=frame_bg, fg=fg_color)
                    elif isinstance(child, tk.Entry):
                        child.config(bg=entry_bg, fg=fg_color, insertbackground=fg_color) # insertbackground for cursor
                    elif isinstance(child, tk.Button):
                        child.config(bg=button_bg, fg=button_fg)
                    elif isinstance(child, tk.Checkbutton):
                        child.config(bg=frame_bg, fg=fg_color, selectcolor=entry_bg)
            elif isinstance(widget, tk.Label):
                widget.config(bg=bg_color, fg=fg_color)
            elif isinstance(widget, tk.Button):
                widget.config(bg=button_bg, fg=button_fg)
            elif isinstance(widget, tk.Checkbutton):
                widget.config(bg=bg_color, fg=fg_color, selectcolor=entry_bg)
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.config(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        
        # Specific styling for process button
        self.process_button.config(bg="#4CAF50" if theme_name == 'light' else "#28A745", fg="white")


    def create_widgets(self):
        # Frame for input/output paths
        path_frame = tk.LabelFrame(self.master, text="Media Paths", padx=10, pady=10, relief="groove")
        path_frame.pack(padx=20, pady=10, fill="x", expand=True)

        tk.Label(path_frame, text="Input Video/Subtitle:").grid(row=0, column=0, sticky="w", pady=5)
        self.input_path_entry = tk.Entry(path_frame, width=60)
        self.input_path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(path_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(path_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_path_entry = tk.Entry(path_frame, width=60)
        self.output_path_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(path_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # Frame for filter settings
        filter_frame = tk.LabelFrame(self.master, text="Content Filters", padx=10, pady=10, relief="groove")
        filter_frame.pack(padx=20, pady=10, fill="x", expand=True)

        # Profanity Filter
        self.profanity_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Enable Profanity Filter", variable=self.profanity_var,
                       command=self.toggle_profanity_controls).grid(row=0, column=0, sticky="w", pady=2)
        
        tk.Label(filter_frame, text="Profane Words (comma-separated):").grid(row=1, column=0, sticky="w", padx=20)
        self.profanity_words_entry = tk.Entry(filter_frame, width=50)
        self.profanity_words_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        tk.Label(filter_frame, text="Replace With:").grid(row=2, column=0, sticky="w", padx=20)
        self.profanity_replace_entry = tk.Entry(filter_frame, width=20)
        self.profanity_replace_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(filter_frame, text="Action:").grid(row=2, column=2, sticky="e")
        self.profanity_action_var = tk.StringVar(value="mute_audio")
        tk.OptionMenu(filter_frame, self.profanity_action_var, "mute_audio", "replace_text").grid(row=2, column=3, sticky="w", padx=5)


        # Nudity Filter
        self.nudity_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Enable Nudity Filter", variable=self.nudity_var,
                       command=self.toggle_nudity_controls).grid(row=3, column=0, sticky="w", pady=2)
        
        tk.Label(filter_frame, text="Threshold (0.0-1.0):").grid(row=4, column=0, sticky="w", padx=20)
        self.nudity_threshold_scale = tk.Scale(filter_frame, from_=0.0, to=1.0, resolution=0.05,
                                                orient="horizontal", length=200, relief="flat", bd=0)
        self.nudity_threshold_scale.grid(row=4, column=1, columnspan=2, sticky="ew")
        
        tk.Label(filter_frame, text="Action:").grid(row=4, column=3, sticky="e")
        self.nudity_action_var = tk.StringVar(value="blur_region")
        tk.OptionMenu(filter_frame, self.nudity_action_var, "blur_region", "skip_scene").grid(row=4, column=4, sticky="w", padx=5)


        # Violence Filter
        self.violence_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Enable Violence Filter", variable=self.violence_var,
                       command=self.toggle_violence_controls).grid(row=5, column=0, sticky="w", pady=2)
        
        tk.Label(filter_frame, text="Threshold (0.0-1.0):").grid(row=6, column=0, sticky="w", padx=20)
        self.violence_threshold_scale = tk.Scale(filter_frame, from_=0.0, to=1.0, resolution=0.05,
                                                 orient="horizontal", length=200, relief="flat", bd=0)
        self.violence_threshold_scale.grid(row=6, column=1, columnspan=2, sticky="ew")
        
        tk.Label(filter_frame, text="Action:").grid(row=6, column=3, sticky="e")
        self.violence_action_var = tk.StringVar(value="skip_scene")
        tk.OptionMenu(filter_frame, self.violence_action_var, "skip_scene", "mute_audio").grid(row=6, column=4, sticky="w", padx=5)

        # Process Button and Progress
        self.progress_label = tk.Label(self.master, text="Status: Ready", anchor="w")
        self.progress_label.pack(padx=20, pady=5, fill="x")

        self.process_button = tk.Button(self.master, text="Process Media", command=self.start_processing_thread,
                                        bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=3)
        self.process_button.pack(pady=10, ipadx=20, ipady=10)

        # Log output area
        self.log_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=8, state='disabled')
        self.log_text.pack(padx=20, pady=10, fill="both", expand=True)

    def load_initial_values(self):
        # Load paths from settings
        self.input_path_entry.insert(0, self.settings.get('default_input_directory', ''))
        self.output_path_entry.insert(0, self.settings.get('default_output_directory', ''))

        # Load filter states and values
        profanity_filter = self.filters.get('profanity', {})
        self.profanity_var.set(profanity_filter.get('enabled', False))
        self.profanity_words_entry.insert(0, ", ".join(profanity_filter.get('word_list', [])))
        self.profanity_replace_entry.insert(0, profanity_filter.get('replace_with', '[censored]'))
        self.profanity_action_var.set(profanity_filter.get('action', 'mute_audio'))
        
        nudity_filter = self.filters.get('nudity', {})
        self.nudity_var.set(nudity_filter.get('enabled', False))
        self.nudity_threshold_scale.set(nudity_filter.get('detection_threshold', 0.75))
        self.nudity_action_var.set(nudity_filter.get('action', 'blur_region'))

        violence_filter = self.filters.get('violence', {})
        self.violence_var.set(violence_filter.get('enabled', False))
        self.violence_threshold_scale.set(violence_filter.get('detection_threshold', 0.65))
        self.violence_action_var.set(violence_filter.get('action', 'skip_scene'))

        # Set initial control states based on loaded settings
        self.toggle_profanity_controls()
        self.toggle_nudity_controls()
        self.toggle_violence_controls()
    
    def toggle_profanity_controls(self):
        """Enables/disables profanity-related controls based on checkbox state."""
        state = "normal" if self.profanity_var.get() else "disabled"
        self.profanity_words_entry.config(state=state)
        self.profanity_replace_entry.config(state=state)
        self.profanity_action_var.set(self.profanity_action_var.get()) # Refresh OptionMenu state
        self.master.children['!labelframe2'].children['!menubutton2'].config(state=state) # Access OptionMenu by internal name

    def toggle_nudity_controls(self):
        """Enables/disables nudity-related controls based on checkbox state."""
        state = "normal" if self.nudity_var.get() else "disabled"
        self.nudity_threshold_scale.config(state=state)
        self.nudity_action_var.set(self.nudity_action_var.get())
        self.master.children['!labelframe2'].children['!menubutton3'].config(state=state)

    def toggle_violence_controls(self):
        """Enables/disables violence-related controls based on checkbox state."""
        state = "normal" if self.violence_var.get() else "disabled"
        self.violence_threshold_scale.config(state=state)
        self.violence_action_var.set(self.violence_action_var.get())
        self.master.children['!labelframe2'].children['!menubutton4'].config(state=state)

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Video or Subtitle File",
            filetypes=[("Media Files", "*.mp4 *.avi *.mkv *.srt *.sub"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_path_entry.delete(0, tk.END)
            self.input_path_entry.insert(0, file_path)

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, dir_path)

    def log_message(self, message):
        """Appends a message to the GUI log area."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Scroll to the end
        self.log_text.config(state='disabled')
        self.master.update_idletasks() # Force GUI update

    def update_progress_label(self, message):
        """Updates the progress label with a new message."""
        self.progress_label.config(text=f"Status: {message}")
        self.master.update_idletasks() # Force GUI update

    def start_processing_thread(self):
        """Starts the media processing in a separate thread to keep GUI responsive."""
        self.process_button.config(state="disabled") # Disable button during processing
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END) # Clear previous logs
        self.log_text.config(state='disabled')
        self.update_progress_label("Starting processing...")

        # Clear placeholder imports if they exist (for re-runs in a single session)
        global metadata_builder, player_overlay
        metadata_builder = None
        player_overlay = None

        processing_thread = threading.Thread(target=self._process_media_task)
        processing_thread.start()

    def _process_media_task(self):
        """Actual media processing logic run in a separate thread."""
        try:
            self._process_media_logic()
        finally:
            self.master.after(0, lambda: self.process_button.config(state="normal")) # Re-enable button on main thread

    def _process_media_logic(self):
        """Contains the core logic for processing media."""
        input_file = self.input_path_entry.get()
        output_dir = self.output_path_entry.get()

        if not input_file or not output_dir:
            self.log_message("Error: Please select both input file and output directory.")
            self.update_progress_label("Ready (Error)")
            return

        # Update filter settings from current GUI state
        self.filters['profanity']['enabled'] = self.profanity_var.get()
        self.filters['profanity']['word_list'] = [w.strip() for w in self.profanity_words_entry.get().split(',') if w.strip()]
        self.filters['profanity']['replace_with'] = self.profanity_replace_entry.get()
        self.filters['profanity']['action'] = self.profanity_action_var.get()

        self.filters['nudity']['enabled'] = self.nudity_var.get()
        self.filters['nudity']['detection_threshold'] = self.nudity_threshold_scale.get()
        self.filters['nudity']['action'] = self.nudity_action_var.get()

        self.filters['violence']['enabled'] = self.violence_var.get()
        self.filters['violence']['detection_threshold'] = self.violence_threshold_scale.get()
        self.filters['violence']['action'] = self.violence_action_var.get()
        
        # Save updated filters
        try:
            save_filters(self.filters)
            self.log_message("Filter settings updated and saved.")
        except Exception as e:
            self.log_message(f"Warning: Could not save filter settings: {e}")

        # Determine if input is video or subtitle
        video_file = None
        subtitle_file = None
        input_extension = os.path.splitext(input_file)[1].lower()

        if input_extension in ('.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'):
            video_file = input_file
            # Try to find a matching subtitle file in the same directory
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            for ext in ['.srt', '.sub', '.vtt']: # Added .vtt for broader support
                candidate_sub = os.path.join(os.path.dirname(input_file), base_name + ext)
                if os.path.exists(candidate_sub):
                    subtitle_file = candidate_sub
                    self.log_message(f"Auto-detected subtitle file: {subtitle_file}")
                    break
            if not subtitle_file:
                self.log_message("No matching subtitle file found in the same directory. Proceeding without subtitles (unless input was a subtitle file).")
        elif input_extension in ('.srt', '.sub', '.vtt'):
            subtitle_file = input_file
            # Try to find a matching video file in the same directory
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            for ext in ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']:
                candidate_video = os.path.join(os.path.dirname(input_file), base_name + ext)
                if os.path.exists(candidate_video):
                    video_file = candidate_video
                    self.log_message(f"Auto-detected video file: {video_file}")
                    break
            if not video_file:
                self.log_message("No matching video file found for the subtitle. Video scanning will be skipped.")
        else:
            self.log_message(f"Error: Unsupported file type for input: {input_extension}. Please select a video or subtitle file.")
            self.update_progress_label("Ready (Error)")
            return

        if not video_file and self.nudity_var.get() or self.violence_var.get():
            self.log_message("Warning: Video scanning cannot be performed without a video file. Disabling Nudity/Violence filters for this run.")
            self.filters['nudity']['enabled'] = False
            self.filters['violence']['enabled'] = False


        # Import and run backend processing
        try:
            self.update_progress_label("Building media metadata...")
            global metadata_builder
            if metadata_builder is None:
                from modules.metadata_builder import build_media_metadata
                metadata_builder = build_media_metadata

            meta = metadata_builder(video_file, subtitle_file, output_dir)
            
            # Use the actual video file name for preview path, even if subtitle was main input
            display_video_name = os.path.splitext(os.path.basename(video_file))[0] if video_file else "unknown_media"
            preview_path = os.path.join(output_dir, display_video_name + '_preview.txt')
            
            self.log_message(f"Processing Complete: Metadata and preview generated.")
            self.log_message(f"Metadata saved to: {os.path.join(output_dir, display_video_name + '.json')}")
            self.log_message(f"Preview report: {preview_path}")
            self.update_progress_label("Metadata Generated. Ready for Playback.")

            # Optionally, offer to launch playback simulation
            if messagebox.askyesno("Playback", "Do you want to simulate playback with filtering?"):
                self.update_progress_label("Starting playback simulation...")
                global player_overlay
                if player_overlay is None:
                    from modules.player_overlay import MediaPlaybackController
                    player_overlay = MediaPlaybackController

                metadata_path = os.path.join(output_dir, display_video_name + '.json')
                
                # Check if metadata file was actually created and has content
                if os.path.exists(metadata_path) and os.path.getsize(metadata_path) > 2: # Check for empty JSON {}
                    controller = player_overlay(video_file if video_file else "simulated_video.mp4", metadata_path)
                    controller.play(self.log_message) # Pass log_message to controller for output
                    self.log_message("Playback simulation finished.")
                else:
                    self.log_message(f"Error: Metadata file not found or is empty at {metadata_path}. Cannot simulate playback.")
            
            self.update_progress_label("Processing complete.")

        except Exception as e:
            self.log_message(f"Error during processing: {e}")
            self.update_progress_label("Ready (Error)")

def launch_tkinter_gui():
    """Initializes and runs the Tkinter GUI."""
    root = tk.Tk()
    app = CleanMediaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # Ensure config files and necessary directories exist on script start
    initialize_config_files()
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/output', exist_ok=True)
    os.makedirs('movie/metadata', exist_ok=True)
    os.makedirs('modules', exist_ok=True) # Ensure modules directory exists

    # Create dummy video/subtitle/metadata files if they don't exist, for consistent startup
    dummy_video = 'movie/input/sample_movie.mp4'
    dummy_subtitle = 'movie/input/sample_movie.srt'
    dummy_metadata_file = 'movie/metadata/sample_movie.json'
    dummy_preview_file = 'movie/metadata/sample_movie_preview.txt'

    if not os.path.exists(dummy_video):
        with open(dummy_video, 'w') as f: f.write("# Placeholder for sample_movie.mp4")
    if not os.path.exists(dummy_subtitle):
        with open(dummy_subtitle, 'w', encoding='utf-8') as f:
            f.write("""1
00:00:01,000 --> 00:00:03,000
This is a damn test.
2
00:00:04,000 --> 00:00:06,000
Oh, hell no.
""")
    if not os.path.exists(dummy_metadata_file):
        with open(dummy_metadata_file, 'w') as f: f.write('{}')
    if not os.path.exists(dummy_preview_file):
        with open(dummy_preview_file, 'w') as f: f.write('Media actions log placeholder.')

    launch_tkinter_gui()
