# CleanMedia/modules/config_manager.py

import json
import yaml
import os

# Define file paths relative to the project root
CONFIG_DIR = 'config'
FILTERS_PATH = os.path.join(CONFIG_DIR, 'filters.json')
SETTINGS_PATH = os.path.join(CONFIG_DIR, 'settings.yaml')

def load_settings():
    """
    Loads global settings from the settings.yaml file.
    If the file does not exist, returns default settings.
    """
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error loading settings.yaml: {e}. Returning default settings.")
            return get_default_settings()
    return get_default_settings()

def save_settings(settings_data):
    """
    Saves global settings to the settings.yaml file.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(settings_data, f, indent=2)
        print(f"Settings saved to: {SETTINGS_PATH}")
    except Exception as e:
        print(f"Error saving settings.yaml: {e}")

def get_default_settings():
    """
    Returns a dictionary of default settings.
    """
    return {
        "default_input_directory": "movie/input",
        "default_output_directory": "movie/output",
        "preferred_player": "vlc",
        "auto_load_filters": True,
        "verbose_logging": False,
        "gui_theme": "light",
        "max_recent_files": 5,
        "playback_speed": 1.0,
        "subtitle_encoding": "utf-8"
    }

def load_filters():
    """
    Loads filter settings from the filters.json file.
    If the file does not exist, returns default filters.
    """
    if os.path.exists(FILTERS_PATH):
        try:
            with open(FILTERS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading filters.json: {e}. Returning default filters.")
            return get_default_filters()
    return get_default_filters()

def save_filters(filters_data):
    """
    Saves filter settings to the filters.json file.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(FILTERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(filters_data, f, indent=2)
        print(f"Filters saved to: {FILTERS_PATH}")
    except Exception as e:
        print(f"Error saving filters.json: {e}")

def get_default_filters():
    """
    Returns a dictionary of default filter settings.
    """
    return {
        "profanity": {
            "enabled": True,
            "word_list": ["damn", "hell", "shit", "fuck", "bitch", "ass"],
            "replace_with": "[censored]",
            "action": "mute_audio"
        },
        "nudity": {
            "enabled": False,
            "detection_threshold": 0.75,
            "action": "blur_region"
        },
        "violence": {
            "enabled": False,
            "detection_threshold": 0.65,
            "action": "skip_scene"
        }
    }

# Ensure config directory and default files exist on first run
def initialize_config_files():
    """Ensures config directory and default filter/settings files exist."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(FILTERS_PATH):
        print("filters.json not found. Creating with default values.")
        save_filters(get_default_filters())
    
    if not os.path.exists(SETTINGS_PATH):
        print("settings.yaml not found. Creating with default values.")
        save_settings(get_default_settings())

# Initialize config files when this module is imported
initialize_config_files()

if __name__ == '__main__':
    # Example usage for testing this module
    print("--- Testing Config Manager ---")

    # Test loading
    settings = load_settings()
    filters = load_filters()
    print("\nLoaded Settings:", settings)
    print("Loaded Filters:", filters)

    # Test modifying and saving settings
    settings['verbose_logging'] = True
    save_settings(settings)
    print("\nSettings after modification and save:", load_settings())

    # Test modifying and saving filters
    filters['profanity']['word_list'].append('asshole')
    filters['nudity']['enabled'] = True
    filters['nudity']['detection_threshold'] = 0.8
    save_filters(filters)
    print("\nFilters after modification and save:", load_filters())

    # Clean up (optional, for testing purposes)
    # os.remove(FILTERS_PATH)
    # os.remove(SETTINGS_PATH)
    # print("\nCleaned up dummy config files.")
