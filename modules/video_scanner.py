# CleanMedia/modules/video_scanner.py

import cv2
import json
import os
from collections import deque

# from tensorflow.keras.models import load_model  # Example for AI model

def load_filters(filters_path='config/filters.json'):
    """Loads filter settings from a JSON file."""
    if os.path.exists(filters_path):
        with open(filters_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def scan_video_for_content(video_path, filters):
    """
    Scans a video file for nudity and violence.  The implementation here
    uses very lightweight heuristics so the function works without heavy
    machine learning dependencies.  It checks the percentage of skin-toned
    pixels to approximate nudity and the percentage of red pixels to
    approximate violence.  These heuristics are obviously simplistic but
    allow the rest of the pipeline to function while a real model is being
    integrated.

    Args:
        video_path (str): Path to the input video file.
        filters (dict): Dictionary containing filter settings.

    Returns:
        list: A list of dictionaries, each detailing a detected action
              (e.g., {"type": "nudity_detection", "start_time": ..., "end_time": ...}).
    """
    print(f"Scanning video: {video_path}")
    actions = []

    nudity_settings = filters.get('nudity', {})
    violence_settings = filters.get('violence', {})

    nudity_enabled = nudity_settings.get('enabled', False)
    nudity_threshold = nudity_settings.get('detection_threshold', 0.8)
    violence_enabled = violence_settings.get('enabled', False)
    violence_threshold = violence_settings.get('detection_threshold', 0.7)

    if not (nudity_enabled or violence_enabled):
        print("Both nudity and violence filters are disabled. Skipping video scan.")
        return []

    # Placeholder for loading AI models
    # try:
    #     nudity_model = load_model('path/to/nudity_detection_model.h5')
    #     violence_model = load_model('path/to/violence_detection_model.h5')
    # except Exception as e:
    #     print(f"Warning: Could not load AI model. Video scanning will be simulated. Error: {e}")
    #     # Set models to None to trigger simulation
    #     nudity_model = None
    #     violence_model = None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return actions

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video FPS: {fps}, Total Frames: {frame_count}")

    frame_interval = max(1, int(fps))  # roughly one frame per second

    skin_lower = (0, 133, 77)
    skin_upper = (255, 173, 127)
    red_lower = (0, 0, 120)
    red_upper = (80, 80, 255)

    def ratio_in_range(img, lower, upper):
        mask = cv2.inRange(img, lower, upper)
        return cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])

    detected = []

    window = deque(maxlen=3)

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        if i % frame_interval == 0:
            current_time_seconds = i / fps
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            skin_ratio = ratio_in_range(ycrcb, skin_lower, skin_upper)
            red_ratio = ratio_in_range(frame, red_lower, red_upper)

            window.append((current_time_seconds, skin_ratio, red_ratio))

            if nudity_enabled and skin_ratio >= nudity_threshold:
                actions.append({
                    "type": "nudity_detection",
                    "start_time": current_time_seconds,
                    "end_time": current_time_seconds + 1,
                    "confidence": skin_ratio,
                    "action_suggestion": nudity_settings.get('action', 'blur')
                })
                print(f"  Nudity heuristic triggered at {current_time_seconds:.2f}s (ratio={skin_ratio:.2f})")

            if violence_enabled and red_ratio >= violence_threshold:
                actions.append({
                    "type": "violence_detection",
                    "start_time": current_time_seconds,
                    "end_time": current_time_seconds + 1,
                    "confidence": red_ratio,
                    "action_suggestion": violence_settings.get('action', 'skip_scene')
                })
                print(f"  Violence heuristic triggered at {current_time_seconds:.2f}s (ratio={red_ratio:.2f})")

    cap.release()
    print(f"Finished video scanning. Found {len(actions)} potential issues.")
    return actions

if __name__ == '__main__':
    # Example usage for testing this module
    dummy_video_path = 'movie/input/your_movie.mp4'

    # Ensure directories exist for the example
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('config', exist_ok=True)

    # Create a dummy filters.json for testing
    dummy_filters = {
        "profanity": {"enabled": False},
        "nudity": {"enabled": True, "detection_threshold": 0.7, "action": "blur"},
        "violence": {"enabled": True, "detection_threshold": 0.6, "action": "skip_scene"}
    }
    with open('config/filters.json', 'w', encoding='utf-8') as f:
        json.dump(dummy_filters, f, indent=2)
    print("Created dummy filters.json")

    # Create a dummy video file (using a placeholder file, as we can't create an actual video here)
    # In a real scenario, 'your_movie.mp4' would need to be a valid video file.
    if not os.path.exists(dummy_video_path):
        with open(dummy_video_path, 'w') as f:
            f.write("# This is a placeholder for a video file.")
        print(f"Created dummy video file: {dummy_video_path}. Please replace with a real video for actual testing.")

    filters = load_filters()
    detected_issues = scan_video_for_content(dummy_video_path, filters)

    print("\n--- Detected Video Content Issues ---")
    if detected_issues:
        for issue in detected_issues:
            print(issue)
    else:
        print("No issues detected (or video file not valid for scanning simulation).")

