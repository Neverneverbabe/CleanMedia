# CleanMedia/modules/subtitle_parser.py

import srt
import json
import re
import os

def load_filters(filters_path='config/filters.json'):
    """Loads filter settings from a JSON file."""
    if os.path.exists(filters_path):
        with open(filters_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def parse_and_filter_subtitles(subtitle_path, filters):
    """
    Parses an SRT file and filters content based on profanity settings.

    Args:
        subtitle_path (str): Path to the input SRT file.
        filters (dict): Dictionary containing filter settings.

    Returns:
        tuple: A tuple containing:
            - list: A list of original srt.Subtitle objects.
            - list: A list of srt.Subtitle objects with filtered text.
            - list: A list of dictionaries detailing mute/replace actions.
    """
    original_subtitles = []
    filtered_subtitles = []
    actions = []

    profanity_settings = filters.get('profanity', {})
    if not profanity_settings.get('enabled', False):
        print("Profanity filter is disabled. Subtitles will not be modified.")
        # If profanity filter is off, just return original subtitles as filtered
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded_subs = list(srt.parse(content))
            return loaded_subs, loaded_subs, []


    word_list = profanity_settings.get('word_list', [])
    replace_with = profanity_settings.get('replace_with', '[CENSORED]')

    # Create a regex pattern for faster matching, case-insensitive, whole words
    # Sort by length descending to handle "hot" before "hotdog" if both are in list
    word_list_sorted = sorted(word_list, key=len, reverse=True)
    pattern = r'\b(' + '|'.join(re.escape(word) for word in word_list_sorted) + r')\b'
    profanity_regex = re.compile(pattern, re.IGNORECASE)

    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        loaded_subs = list(srt.parse(content))

        for sub in loaded_subs:
            original_subtitles.append(sub)
            filtered_text = sub.content
            
            # Find all matches
            matches = list(profanity_regex.finditer(filtered_text))

            if matches:
                # Replace matched words and record actions
                for match in matches:
                    matched_word = match.group(0)
                    start_index = match.start()
                    end_index = match.end()

                    # Record the action
                    actions.append({
                        "type": "profanity_mute",
                        "start_time": sub.start.total_seconds(),
                        "end_time": sub.end.total_seconds(),
                        "original_text": sub.content,
                        "matched_word": matched_word,
                        "action_taken": f"replaced '{matched_word}' with '{replace_with}'"
                    })
                    
                    # Perform the replacement
                    # Using sub() to replace all occurrences
                    filtered_text = profanity_regex.sub(replace_with, filtered_text)
                    
                # Create a new subtitle object with the modified text
                filtered_subtitles.append(srt.Subtitle(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    content=filtered_text,
                    proprietary=sub.proprietary
                ))
            else:
                # If no profanity, keep the subtitle as is
                filtered_subtitles.append(sub)

    except FileNotFoundError:
        print(f"Error: Subtitle file not found at {subtitle_path}")
    except Exception as e:
        print(f"An error occurred while parsing subtitles: {e}")

    return original_subtitles, filtered_subtitles, actions

def save_filtered_subtitles(subtitles, output_path):
    """Saves a list of srt.Subtitle objects to an SRT file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subtitles))
        print(f"Filtered subtitles saved to {output_path}")
    except Exception as e:
        print(f"Error saving filtered subtitles: {e}")

if __name__ == '__main__':
    # Example usage for testing this module
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
    dummy_subtitle_path = 'movie/input/your_movie.srt'
    output_filtered_srt_path = 'movie/output/your_movie_filtered.srt'
    
    # Ensure directories exist for the example
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/output', exist_ok=True)
    os.makedirs('config', exist_ok=True)

    # Create a dummy subtitle file
    with open(dummy_subtitle_path, 'w', encoding='utf-8') as f:
        f.write(dummy_subtitle_content.strip())
    print(f"Created dummy subtitle file: {dummy_subtitle_path}")

    # Create a dummy filters.json for testing
    dummy_filters = {
        "profanity": {
            "enabled": True,
            "word_list": ["damn", "hell", "fuck", "shit"],
            "replace_with": "[bleep]"
        },
        "nudity": {"enabled": False},
        "violence": {"enabled": False}
    }
    with open('config/filters.json', 'w', encoding='utf-8') as f:
        json.dump(dummy_filters, f, indent=2)
    print("Created dummy filters.json")

    filters = load_filters()
    original, filtered, actions = parse_and_filter_subtitles(dummy_subtitle_path, filters)

    print("\n--- Original Subtitles ---")
    for sub in original:
        print(f"[{sub.start} --> {sub.end}] {sub.content}")

    print("\n--- Filtered Subtitles ---")
    for sub in filtered:
        print(f"[{sub.start} --> {sub.end}] {sub.content}")
    
    print("\n--- Detected Actions ---")
    for action in actions:
        print(action)

    save_filtered_subtitles(filtered, output_filtered_srt_path)
