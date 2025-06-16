# CleanMedia/main.py

import os
import sys

# Real GUI launcher
def launch_gui():
    from gui.launcher_gui import launch_tkinter_gui
    launch_tkinter_gui()

# Real CLI logic
def run_cli():
    import argparse
    parser = argparse.ArgumentParser(description="CleanMedia CLI")
    parser.add_argument('--video', type=str, help='Path to input video file')
    parser.add_argument('--subtitle', type=str, help='Path to input subtitle file (optional)')
    parser.add_argument('--output', type=str, default='movie/metadata', help='Output directory for metadata and preview')
    parser.add_argument('--play', action='store_true', help='Simulate playback after processing')
    args = parser.parse_args(sys.argv[2:] if sys.argv[1] == '--cli' else sys.argv[1:])

    if not args.video:
        print("Error: --video argument is required.")
        return
    video_file = args.video
    subtitle_file = args.subtitle
    output_dir = args.output

    from modules.metadata_builder import build_media_metadata
    meta = build_media_metadata(video_file, subtitle_file, output_dir)
    preview_path = os.path.join(output_dir, os.path.splitext(os.path.basename(video_file))[0] + '_preview.txt')
    print(f"Metadata and preview generated. Preview: {preview_path}")
    if args.play:
        from modules.player_overlay import MediaPlaybackController
        metadata_path = os.path.join(output_dir, os.path.splitext(os.path.basename(video_file))[0] + '.json')
        controller = MediaPlaybackController(video_file, metadata_path)
        controller.play()

def main():
    # Basic logic to determine if GUI should be launched or CLI
    # You can expand this to parse command-line arguments to choose mode
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli()
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
