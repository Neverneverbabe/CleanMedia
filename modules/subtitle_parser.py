# CleanMedia/modules/subtitle_parser.py

import srt
import json
import re
import os

# No need to load_filters here, it will be passed from metadata_builder

def parse_and_filter_subtitles(subtitle_path, filters, log_callback=None):
    """
    Parses an SRT file and filters content based on profanity settings.

    Args:
        subtitle_path (str): Path to the input SRT file.
        filters (dict): Dictionary containing filter settings (profanity, nudity, violence).
        log_callback (callable, optional): Function to call for logging messages to GUI.

    Returns:
        tuple: A tuple containing:
            - list: A list of original srt.Subtitle objects.
            - list: A list of srt.Subtitle objects with filtered text.
            - list: A list of dictionaries detailing mute/replace actions.
    """
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)

    original_subtitles = []
    filtered_subtitles = []
    actions = []

    profanity_settings = filters.get('profanity', {})
    profanity_enabled = profanity_settings.get('enabled', False)
    word_list = profanity_settings.get('word_list', [])
    replace_with = profanity_settings.get('replace_with', '[CENSORED]')
    profanity_action = profanity_settings.get('action', 'mute_audio')


    if not profanity_enabled:
        log("Profanity filter is disabled. Subtitles will not be modified for profanity.")
        # If profanity filter is off, just return original subtitles as filtered
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
                loaded_subs = list(srt.parse(content))
                return loaded_subs, loaded_subs, []
        except FileNotFoundError:
            log(f"Error: Subtitle file not found at {subtitle_path}")
            return [], [], []
        except Exception as e:
            log(f"An error occurred while parsing subtitles: {e}")
            return [], [], []


    if not word_list:
        log("Profanity filter is enabled but word list is empty. No words to filter.")
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
                loaded_subs = list(srt.parse(content))
                return loaded_subs, loaded_subs, []
        except FileNotFoundError:
            log(f"Error: Subtitle file not found at {subtitle_path}")
            return [], [], []
        except Exception as e:
            log(f"An error occurred while parsing subtitles: {e}")
            return [], [], []


    # Create a regex pattern for faster matching, case-insensitive, whole words
    # Sort by length descending to handle "hot" before "hotdog" if both are in list
    word_list_sorted = sorted(word_list, key=len, reverse=True)
    # Using \b for word boundaries. For example, "hell" will not match "hello".
    pattern = r'\b(' + '|'.join(re.escape(word) for word in word_list_sorted) + r')\b'
    profanity_regex = re.compile(pattern, re.IGNORECASE)

    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        loaded_subs = list(srt.parse(content))

        for sub in loaded_subs:
            original_subtitles.append(sub)
            current_filtered_text = sub.content # Start with original content for this subtitle
            
            # Find all matches in the current subtitle content
            matches = list(profanity_regex.finditer(current_filtered_text))

            if matches:
                # To correctly replace multiple occurrences without messing up indices,
                # it's often easier to build the new string or replace in one go using sub().
                # Record actions first based on original text.
                for match in matches:
                    matched_word = match.group(0)
                    
                    actions.append({
                        "type": "profanity_mute", # Naming convention for action type
                        "start_time": sub.start.total_seconds(),
                        "end_time": sub.end.total_seconds(),
                        "original_text": sub.content,
                        "matched_word": matched_word,
                        "action_taken": f"replaced '{matched_word}' with '{replace_with}'",
                        "action_suggestion": profanity_action # Store the chosen action from filter settings
                    })
                
                # Perform the replacement on the text that will be used for the filtered subtitle
                # This replaces all matched words in the current subtitle's content
                current_filtered_text = profanity_regex.sub(replace_with, current_filtered_text)
                
                # Create a new subtitle object with the modified text
                filtered_subtitles.append(srt.Subtitle(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    content=current_filtered_text,
                    proprietary=sub.proprietary
                ))
            else:
                # If no profanity, keep the subtitle as is
                filtered_subtitles.append(sub)

    except FileNotFoundError:
        log(f"Error: Subtitle file not found at {subtitle_path}")
        return [], [], []
    except Exception as e:
        log(f"An error occurred while parsing subtitles: {e}")
        return [], [], []

    return original_subtitles, filtered_subtitles, actions

def save_filtered_subtitles(subtitles, output_path, log_callback=None):
    """Saves a list of srt.Subtitle objects to an SRT file."""
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subtitles))
        log(f"Filtered subtitles saved to {output_path}")
    except Exception as e:
        log(f"Error saving filtered subtitles: {e}")

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
    dummy_subtitle_path = 'movie/input/sample_movie.srt' # Consistent dummy name
    output_filtered_srt_path = 'movie/output/sample_movie_filtered.srt' # Consistent dummy name
    
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
            "replace_with": "[bleep]",
            "action": "mute_audio" # Added action for testing
        },
        "nudity": {"enabled": False},
        "violence": {"enabled": False}
    }
    with open('config/filters.json', 'w', encoding='utf-8') as f:
        json.dump(dummy_filters, f, indent=2)
    print("Created dummy filters.json")

    # Load filters directly or pass the dummy_filters
    filters_for_test = dummy_filters # Use the local dummy for this test run

    original, filtered, actions = parse_and_filter_subtitles(dummy_subtitle_path, filters_for_test)

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
