# CleanMedia/main.py

import os
import sys
import argparse

from modules.metadata_builder import build_media_metadata
from modules.player_overlay import MediaPlaybackController

# Placeholder for GUI launcher
def launch_gui():
    print("Launching GUI...")
    # In a real application, you would import and run the Tkinter GUI here:
    # from gui.launcher_gui import launch_tkinter_gui
    # launch_tkinter_gui()

def build_command(args):
    """Handle the 'build' CLI command."""
    build_media_metadata(args.video, args.subtitle, args.output)


def play_command(args):
    """Handle the 'play' CLI command."""
    controller = MediaPlaybackController(args.video, args.metadata)
    controller.play()
    controller.stop()

def run_cli(argv):
    parser = argparse.ArgumentParser(description="CleanMedia command line")
    subparsers = parser.add_subparsers(dest="command")

    build_p = subparsers.add_parser("build", help="Generate metadata")
    build_p.add_argument("video")
    build_p.add_argument("--subtitle", "-s", default=None)
    build_p.add_argument("--output", "-o", default="movie/metadata")
    build_p.set_defaults(func=build_command)

    play_p = subparsers.add_parser("play", help="Play video applying actions")
    play_p.add_argument("video")
    play_p.add_argument("metadata")
    play_p.set_defaults(func=play_command)

    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

def main():
    # Decide whether to run CLI or GUI
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli(sys.argv[2:])
    else:
        # Default to GUI if no specific mode is requested
        launch_gui()

if __name__ == "__main__":
    # Ensure necessary directories exist
    os.makedirs('config', exist_ok=True)
    os.makedirs('gui', exist_ok=True)
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/output', exist_ok=True)
    os.makedirs('movie/metadata', exist_ok=True)
    os.makedirs('modules', exist_ok=True)

    # Create dummy files if they don't exist
    for path in [
        'config/filters.json',
        'config/settings.yaml',
        'gui/launcher_gui.py',
        'modules/subtitle_parser.py',
        'modules/video_scanner.py',
        'modules/metadata_builder.py',
        'modules/player_overlay.py'
    ]:
        if not os.path.exists(path):
            with open(path, 'w') as f:
                if 'json' in path:
                    f.write('{}')
                elif 'yaml' in path:
                    f.write('')
                else: # Python files
                    f.write('# This is a placeholder file.')

    main()
