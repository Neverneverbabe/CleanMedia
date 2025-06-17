# CleanMedia/modules/metadata_builder.py

import json
import os
import time
from datetime import timedelta

# Import from the centralized config manager
from modules.config_manager import load_filters

# Assuming these modules exist and have the specified functions
# We'll import them inside build_media_metadata to avoid circular imports
# when config_manager imports them or launcher_gui imports metadata_builder.
subtitle_parser = None
video_scanner = None

def format_timedelta(td):
    """Formats a timedelta object into HH:MM:SS.mmm string."""
    total_seconds = int(td.total_seconds())
    milliseconds = int((td.total_seconds() * 1000) % 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def build_media_metadata(video_path, subtitle_path=None, output_dir='movie/metadata', log_callback=None):
    """
    Builds a comprehensive metadata JSON for a media file, combining
    subtitle filtering results and video scanning results.

    Args:
        video_path (str): Path to the input video file.
        subtitle_path (str, optional): Path to the input subtitle file (SRT).
        output_dir (str, optional): Directory to save metadata and preview files.
        log_callback (callable, optional): Function to call for logging messages to GUI.

    Returns:
        dict: The generated metadata dictionary.
    """
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)

    log(f"Building metadata for video: {video_path}")
    if subtitle_path:
        log(f"Using subtitles from: {subtitle_path}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load filter settings from the centralized manager
    filters = load_filters()
    if not filters:
        log("Warning: Could not load filters.json. Proceeding with default/empty filters.")

    media_filename = os.path.splitext(os.path.basename(video_path))[0]
    metadata_json_path = os.path.join(output_dir, f"{media_filename}.json")
    preview_txt_path = os.path.join(output_dir, f"{media_filename}_preview.txt")

    # Initialize metadata structure
    metadata = {
        "media_file": os.path.basename(video_path),
        "subtitle_file": os.path.basename(subtitle_path) if subtitle_path else None,
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "filters_applied": {
            "profanity": filters.get('profanity', {}).get('enabled', False),
            "nudity": filters.get('nudity', {}).get('enabled', False),
            "violence": filters.get('violence', {}).get('enabled', False)
        },
        "actions": [] # This will store all identified mute/skip/replace actions
    }

    preview_log_lines = [f"CleanMedia Processing Report for: {metadata['media_file']}\n"]
    preview_log_lines.append(f"Processed At: {metadata['processed_at']}\n")
    preview_log_lines.append(f"Filters Enabled: Profanity={metadata['filters_applied']['profanity']}, "
                             f"Nudity={metadata['filters_applied']['nudity']}, "
                             f"Violence={metadata['filters_applied']['violence']}\n")
    preview_log_lines.append("-" * 50 + "\n")

    # 1. Process Subtitles for Profanity
    subtitle_actions = []
    profanity_enabled = filters.get('profanity', {}).get('enabled', False)
    if subtitle_path and os.path.exists(subtitle_path) and profanity_enabled:
        log("Processing subtitles for profanity...")
        global subtitle_parser
        if subtitle_parser is None:
            from modules.subtitle_parser import parse_and_filter_subtitles
            subtitle_parser = parse_and_filter_subtitles

        _, filtered_subs, sub_actions = subtitle_parser(subtitle_path, filters, log_callback)
        subtitle_actions.extend(sub_actions)
        metadata['actions'].extend(sub_actions)

        preview_log_lines.append("Subtitle Profanity Detections:\n")
        if sub_actions:
            for action in sub_actions:
                start_hms = format_timedelta(timedelta(seconds=action['start_time']))
                end_hms = format_timedelta(timedelta(seconds=action['end_time']))
                preview_log_lines.append(f"  [{start_hms} - {end_hms}] Type: {action['type']} "
                                         f"Original: '{action['original_text']}' -> Action: {action['action_taken']}\n")
        else:
            preview_log_lines.append("  No profanity detected in subtitles.\n")
        preview_log_lines.append("\n")
    elif subtitle_path and not os.path.exists(subtitle_path):
        log(f"Subtitle file not found at {subtitle_path}. Skipping subtitle processing.")
        preview_log_lines.append(f"Subtitle file not found at {subtitle_path}. Subtitle processing skipped.\n\n")
    else:
        log("Subtitle path not provided or profanity filter disabled. Skipping subtitle processing.")
        preview_log_lines.append("Subtitle processing skipped (no subtitle provided or filter disabled).\n\n")

    # 2. Scan Video for Nudity/Violence
    video_content_actions = []
    nudity_enabled = filters.get('nudity', {}).get('enabled', False)
    violence_enabled = filters.get('violence', {}).get('enabled', False)

    if os.path.exists(video_path) and (nudity_enabled or violence_enabled):
        log("Scanning video for nudity and violence...")
        global video_scanner
        if video_scanner is None:
            from modules.video_scanner import scan_video_for_content
            video_scanner = scan_video_for_content

        video_actions = video_scanner(video_path, filters, log_callback)
        video_content_actions.extend(video_actions)
        metadata['actions'].extend(video_actions)

        preview_log_lines.append("Video Content Detections (Nudity/Violence):\n")
        if video_actions:
            # Group consecutive actions of the same type for better readability
            grouped_actions = []
            if video_actions:
                current_group = None
                # Sort actions by start time to ensure correct grouping
                sorted_video_actions = sorted(video_actions, key=lambda x: x['start_time'])
                for action in sorted_video_actions:
                    # Merge if same type and overlaps or is very close (e.g., within 1 second)
                    if current_group and action['type'] == current_group['type'] and \
                       action['start_time'] <= current_group['end_time'] + 1:
                        current_group['end_time'] = max(current_group['end_time'], action['end_time'])
                    else:
                        if current_group:
                            grouped_actions.append(current_group)
                        current_group = action.copy()
                if current_group:
                    grouped_actions.append(current_group)

            for action in grouped_actions:
                start_hms = format_timedelta(timedelta(seconds=action['start_time']))
                end_hms = format_timedelta(timedelta(seconds=action['end_time']))
                preview_log_lines.append(f"  [{start_hms} - {end_hms}] Type: {action['type']} "
                                         f"Confidence: {action.get('confidence', 'N/A'):.2f} "
                                         f"Suggested Action: {action.get('action_suggestion', 'N/A')}\n")
        else:
            preview_log_lines.append("  No nudity or violence detected in video.\n")
        preview_log_lines.append("\n")
    elif not os.path.exists(video_path):
        log(f"Video file not found at {video_path}. Skipping video scanning.")
        preview_log_lines.append(f"Video file not found at {video_path}. Video scanning skipped.\n\n")
    else:
        log("Nudity/Violence filters disabled or no video provided. Skipping video scanning.")
        preview_log_lines.append("Video scanning skipped (filters disabled or no video provided).\n\n")

    # Sort all actions by start_time for chronological processing
    metadata['actions'].sort(key=lambda x: x['start_time'])

    # Save metadata JSON
    try:
        with open(metadata_json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
        log(f"Metadata saved to: {metadata_json_path}")
    except Exception as e:
        log(f"Error saving metadata JSON: {e}")

    # Save human-readable preview log
    try:
        with open(preview_txt_path, 'w', encoding='utf-8') as f:
            f.writelines(preview_log_lines)
        log(f"Preview log saved to: {preview_txt_path}")
    except Exception as e:
        log(f"Error saving preview log: {e}")

    return metadata

if __name__ == '__main__':
    # Example usage for testing this module
    dummy_video = 'movie/input/sample_movie.mp4'
    dummy_subtitle = 'movie/input/sample_movie.srt'
    output_meta_dir = 'movie/metadata'

    # Ensure necessary directories exist
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/metadata', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    os.makedirs('modules', exist_ok=True)

    # Create dummy video and subtitle files if they don't exist
    if not os.path.exists(dummy_video):
        with open(dummy_video, 'w') as f:
            f.write("# This is a placeholder for a video file.")
        print(f"Created placeholder: {dummy_video}")
    
    if not os.path.exists(dummy_subtitle):
        dummy_subtitle_content = """
1
00:00:01,000 --> 00:00:03,500
This is a damn good movie.

2
00:00:04,000 --> 00:00:06,000
Oh, hell no, not again.

3
00:00:07,000 --> 00:00:09,000
No profanity here.

4
00:00:10,000 --> 00:00:12,000
What the fuck was that shit?
"""
        with open(dummy_subtitle, 'w', encoding='utf-8') as f:
            f.write(dummy_subtitle_content.strip())
        print(f"Created placeholder: {dummy_subtitle}")

    # Create dummy filters.json for testing
    dummy_filters = {
        "profanity": {
            "enabled": True,
            "word_list": ["damn", "hell", "fuck", "shit"],
            "replace_with": "[BLOCKED]",
            "action": "mute_audio"
        },
        "nudity": {
            "enabled": True,
            "detection_threshold": 0.7,
            "action": "blur_region"
        },
        "violence": {
            "enabled": True,
            "detection_threshold": 0.6,
            "action": "skip_scene"
        }
    }
    with open('config/filters.json', 'w', encoding='utf-8') as f:
        json.dump(dummy_filters, f, indent=2)
    print("Created dummy filters.json for test.")

    # Call the build function
    metadata_result = build_media_metadata(dummy_video, dummy_subtitle, output_meta_dir)
    print("\n--- Final Metadata ---")
    print(json.dumps(metadata_result, indent=4))
