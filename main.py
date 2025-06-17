# CleanMedia/main.py

import os
import sys
import argparse

# Import the centralized config manager to ensure files are initialized
from modules.config_manager import initialize_config_files, load_filters, load_settings, save_filters

# Real GUI launcher
def launch_gui():
    from gui.launcher_gui import launch_tkinter_gui
    launch_tkinter_gui()

# Real CLI logic
def run_cli():
    parser = argparse.ArgumentParser(description="CleanMedia CLI")
    parser.add_argument('--video', type=str, help='Path to input video file')
    parser.add_argument('--subtitle', type=str, help='Path to input subtitle file (optional)')
    parser.add_argument('--output', type=str, default='movie/metadata', help='Output directory for metadata and preview')
    parser.add_argument('--play', action='store_true', help='Simulate playback after processing')
    
    # CLI arguments for filter settings
    parser.add_argument('--profanity-enable', action='store_true', help='Enable profanity filter')
    parser.add_argument('--profanity-words', type=str, help='Comma-separated list of profane words')
    parser.add_argument('--profanity-replace', type=str, help='String to replace profanity with')
    parser.add_argument('--profanity-action', type=str, choices=['mute_audio', 'replace_text'], default='mute_audio', help='Action for profanity')

    parser.add_argument('--nudity-enable', action='store_true', help='Enable nudity filter')
    parser.add_argument('--nudity-threshold', type=float, help='Nudity detection threshold (0.0-1.0)')
    parser.add_argument('--nudity-action', type=str, choices=['blur_region', 'skip_scene'], default='blur_region', help='Action for nudity')

    parser.add_argument('--violence-enable', action='store_true', help='Enable violence filter')
    parser.add_argument('--violence-threshold', type=float, help='Violence detection threshold (0.0-1.0)')
    parser.add_argument('--violence-action', type=str, choices=['skip_scene', 'mute_audio'], default='skip_scene', help='Action for violence')


    args = parser.parse_args(sys.argv[2:] if sys.argv[1] == '--cli' else sys.argv[1:])

    if not args.video:
        print("Error: --video argument is required for CLI mode.")
        return

    # Load existing filters, then override with CLI arguments
    filters = load_filters()

    if args.profanity_enable:
        filters['profanity']['enabled'] = True
    if args.profanity_words:
        filters['profanity']['word_list'] = [w.strip() for w in args.profanity_words.split(',') if w.strip()]
    if args.profanity_replace:
        filters['profanity']['replace_with'] = args.profanity_replace
    if args.profanity_action:
        filters['profanity']['action'] = args.profanity_action

    if args.nudity_enable:
        filters['nudity']['enabled'] = True
    if args.nudity_threshold is not None:
        filters['nudity']['detection_threshold'] = args.nudity_threshold
    if args.nudity_action:
        filters['nudity']['action'] = args.nudity_action

    if args.violence_enable:
        filters['violence']['enabled'] = True
    if args.violence_threshold is not None:
        filters['violence']['detection_threshold'] = args.violence_threshold
    if args.violence_action:
        filters['violence']['action'] = args.violence_action
    
    # Save the updated filters for this run (and future runs if desired)
    save_filters(filters)

    video_file = args.video
    subtitle_file = args.subtitle
    output_dir = args.output

    # Determine if video file exists to avoid trying to scan non-existent files
    if not os.path.exists(video_file) and (filters['nudity']['enabled'] or filters['violence']['enabled']):
        print(f"Warning: Video file '{video_file}' not found. Nudity and Violence scanning will be skipped.")
        # Temporarily disable filters for the current run if video is missing
        filters['nudity']['enabled'] = False
        filters['violence']['enabled'] = False
    
    # Determine if subtitle file exists
    if subtitle_file and not os.path.exists(subtitle_file):
        print(f"Warning: Subtitle file '{subtitle_file}' not found. Subtitle parsing will be skipped.")
        subtitle_file = None # Ensure it's treated as None

    from modules.metadata_builder import build_media_metadata
    meta = build_media_metadata(video_file, subtitle_file, output_dir)
    
    # Use the actual video file name for preview path, even if subtitle was main input
    display_video_name = os.path.splitext(os.path.basename(video_file))[0] if video_file else "cli_processed_media"
    preview_path = os.path.join(output_dir, display_video_name + '_preview.txt')
    print(f"Metadata and preview generated. Preview: {preview_path}")

    if args.play:
        from modules.player_overlay import MediaPlaybackController
        metadata_path = os.path.join(output_dir, display_video_name + '.json')
        # Check if metadata file was actually created and has content
        if os.path.exists(metadata_path) and os.path.getsize(metadata_path) > 2: # Check for empty JSON {}
            controller = MediaPlaybackController(video_file, metadata_path)
            controller.play(log_callback=print) # Pass print for CLI logging
        else:
            print(f"Error: Metadata file not found or is empty at {metadata_path}. Cannot simulate playback.")


def main():
    # Ensure necessary directories and config files exist before anything else
    os.makedirs('config', exist_ok=True)
    os.makedirs('gui', exist_ok=True) # Ensure gui directory exists for launcher_gui
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/output', exist_ok=True)
    os.makedirs('movie/metadata', exist_ok=True)
    os.makedirs('modules', exist_ok=True)
    initialize_config_files() # Call the function from config_manager

    # Basic logic to determine if GUI should be launched or CLI
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli()
    else:
        # Default to GUI if no specific mode is requested
        launch_gui()

if __name__ == "__main__":
    main()
