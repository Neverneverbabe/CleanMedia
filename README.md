CleanMedia
CleanMedia is a Python application designed to help you filter media content (videos and subtitles) based on user-defined preferences for profanity, nudity, and violence. It offers both a command-line interface (CLI) and a graphical user interface (GUI).

Project Structure
CleanMedia/
│
├── main.py
├── requirements.txt
├── README.md
│
├── .venv/
│
├── config/
│   ├── filters.json
│   └── settings.yaml
│
├── gui/
│   └── launcher_gui.py
│
├── movie/
│   ├── input/
│   │   ├── your_movie.mp4
│   │   └── your_movie.srt
│   │
│   ├── output/
│   │   └── your_movie_filtered.mp4
│   │
│   └── metadata/
│       ├── your_movie.json
│       └── your_movie_preview.txt
│
└── modules/
    ├── subtitle_parser.py
    ├── video_scanner.py
    ├── metadata_builder.py
    └── player_overlay.py

Setup Guide
Follow these steps to set up and run CleanMedia:

1. Clone the Repository (Optional, if you're not building from scratch)
If you're cloning an existing repository, use:

git clone <repository_url>
cd CleanMedia

2. Create a Python Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies:

python -m venv .venv

3. Activate the Virtual Environment
On Windows:

.venv\Scripts\activate

On macOS/Linux:

source .venv/bin/activate

4. Install Dependencies
Once your virtual environment is active, install the required packages:

pip install -r requirements.txt

Usage

Launching the GUI
To run the graphical user interface (GUI), simply execute main.py without any arguments:

python main.py

Running in CLI Mode
To run CleanMedia in command-line interface (CLI) mode:

python main.py --cli --video path/to/your_movie.mp4 --subtitle path/to/your_movie.srt --output movie/metadata --play

`--video` (required): Path to the input video file.
`--subtitle` (optional): Path to the subtitle file.
`--output` (optional): Output directory for metadata and preview (default: movie/metadata).
`--play` (optional): Simulate playback after processing.

How It Works (Pipeline)

Input: You provide a video file (and optionally a subtitle file).
Processing: The pipeline parses subtitles, scans video, and builds metadata and a preview report.
Playback: You can simulate playback with filtering actions using the player overlay.

Configuration
config/filters.json
This file will store your preferences for filtering content, such as lists of profane words or thresholds for detecting nudity/violence.

{
  "profanity": {
    "enabled": true,
    "word_list": ["damn", "hell", "shit", "fuck"],
    "replace_with": "[bleep]"
  },
  "nudity": {
    "enabled": false,
    "detection_threshold": 0.7
  },
  "violence": {
    "enabled": false,
    "detection_threshold": 0.6
  }
}

config/settings.yaml
This file will contain global user preferences, such as default input/output paths or playback options.

# Default input directory for movies
default_input_path: "movie/input"
# Default output directory for filtered content
default_output_path: "movie/output"
# Playback options (e.g., using VLC player)
playback_engine: "vlc"

How It Works (High-Level)
Input: You provide a video file (e.g., .mp4) and optionally a subtitle file (e.g., .srt).

Scanning:

subtitle_parser.py: Scans subtitles for profane words based on filters.json and prepares an action list for muting/replacing.

video_scanner.py: (Future development) Uses AI models to analyze video frames for nudity or violence and identifies corresponding time segments.

Metadata Generation: metadata_builder.py combines findings from subtitle parsing and video scanning into a your_movie.json file, which includes timestamps and actions (mute, skip, replace). A human-readable preview (your_movie_preview.txt) is also generated.

Playback/Export:

player_overlay.py: (Optional) An advanced feature to control a media player (like VLC) in real-time based on the generated metadata, muting audio or skipping scenes.

Alternatively, you can use the metadata to process and export a your_movie_filtered.mp4 with segments removed or audio muted.

Contributing
(Section for future contributions)

License
(Section for project license)
