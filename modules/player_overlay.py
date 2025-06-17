# CleanMedia/modules/player_overlay.py

import json
import time
import os
import yaml

# Import from the centralized config manager
from modules.config_manager import load_settings

# The actual vlc library cannot be installed/used in this environment,
# so we will keep the simulation.
# try:
#     import vlc
# except ImportError:
#     print("Warning: python-vlc not installed. Real-time playback control will be simulated.")
#     vlc = None # Set vlc to None if import fails

class MediaPlaybackController:
    def __init__(self, video_path, metadata_path):
        self.video_path = video_path
        self.metadata = self._load_metadata(metadata_path)
        self.settings = load_settings()
        self.player = None
        self.instance = None # Placeholder for vlc.Instance()
        self.current_action_index = 0
        self.last_action_time = -1 # To prevent re-triggering actions in the same second
        self.log_callback = None # Will be set by the caller (GUI)

        if not self.metadata:
            self._log(f"Error: Could not load metadata from {metadata_path}. Playback will be unfiltered.")
        
        # Ensure actions are sorted by start_time
        self.actions = sorted(self.metadata.get('actions', []), key=lambda x: x['start_time']) if self.metadata else []
        self._log(f"Loaded {len(self.actions)} actions for media: {os.path.basename(video_path)}")

    def _load_metadata(self, metadata_path):
        """Loads media metadata from a JSON file."""
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                self._log(f"Error decoding metadata JSON from {metadata_path}: {e}")
                return None
        return None

    def _log(self, message):
        """Internal logging function, uses callback if available, else prints."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def initialize_player(self):
        """Initializes the VLC player instance (simulated)."""
        # if vlc:
        #     self.instance = vlc.Instance()
        #     self.player = self.instance.media_player_new()
        #     media = self.instance.media_new(self.video_path)
        #     self.player.set_media(media)
        #     self._log(f"VLC player initialized for {self.video_path}")
        # else:
        self._log("VLC not available or simulation mode. Player initialization simulated.")
        self.player = "simulated_player" # Placeholder for simulation

    def play(self, log_callback=None):
        """
        Starts media playback simulation.
        Args:
            log_callback (callable, optional): Function to call for logging messages to GUI.
        """
        self.log_callback = log_callback
        self.initialize_player()
        if self.player == "simulated_player":
            self._log("\n--- Simulating Media Playback ---")
            self._log("Note: This is a simulation. For actual playback control, install 'python-vlc' and have VLC player installed.")
            self._simulate_playback()
        # elif self.player:
        #     self.player.play()
        #     self._monitor_playback()

    def _simulate_playback(self):
        """Simulates playback and applies actions based on timestamps."""
        # For simplicity, let's assume a fixed duration for the video in simulation
        # In a real scenario, you'd get this from the VLC player or video analysis.
        simulated_duration = 60 # 1 minute for simulation, can be adjusted for testing

        start_time = time.time()
        current_playback_time = 0.0

        # Find the max end time from actions to make simulation duration more realistic
        if self.actions:
            max_action_end_time = max(action['end_time'] for action in self.actions)
            simulated_duration = max(simulated_duration, max_action_end_time + 5) # Add 5 seconds buffer

        while current_playback_time < simulated_duration:
            elapsed_real_time = time.time() - start_time
            current_playback_time = elapsed_real_time # 1:1 simulation of time

            # Check for actions
            self._check_and_apply_actions(current_playback_time)

            # Update console/log less frequently to avoid excessive output
            if int(current_playback_time * 10) % 10 == 0: # Update every second
                self._log(f"Simulating Playback: {current_playback_time:.1f}s / {simulated_duration:.1f}s")
            
            time.sleep(0.1) # Simulate frame rate / update interval

            if current_playback_time >= simulated_duration:
                break
        self._log("\nSimulation Finished.")

    # def _monitor_playback(self):
    #     """Monitors real VLC player playback and applies actions."""
    #     while self.player.is_playing():
    #         current_time_ms = self.player.get_time()
    #         current_playback_time = current_time_ms / 1000.0 # Convert to seconds
    #         self._check_and_apply_actions(current_playback_time)
    #         time.sleep(0.1) # Check every 100ms
    #     self._log("Playback finished.")

    def _check_and_apply_actions(self, current_playback_time):
        """Checks for pending actions and applies them."""
        # Only process if current_playback_time has advanced significantly since last check
        # Use a small epsilon for float comparison to avoid re-triggering for very small time changes
        if current_playback_time <= self.last_action_time + 0.05:
            return

        # Iterate through actions from the current_action_index to optimize
        while self.current_action_index < len(self.actions):
            action = self.actions[self.current_action_index]
            # If current time is within the action's active window
            if action['start_time'] <= current_playback_time < action['end_time']:
                self._apply_action(action, current_playback_time)
                self.last_action_time = current_playback_time # Mark action as applied at this time
                # We might have multiple actions starting at the same time or overlapping,
                # so don't increment index immediately if more overlap could occur.
                # For simplicity here, we'll process one and then move to the next.
                self.current_action_index += 1 
                return # Only apply one action per check interval to avoid overlapping issues
            elif action['start_time'] > current_playback_time:
                # Actions are sorted, so if the current action is in the future,
                # no need to check further for this time step.
                break 
            else: # current_playback_time is past this action's end_time, move to next
                self.current_action_index += 1


    def _apply_action(self, action, current_playback_time):
        """Applies a specific filtering action."""
        action_type = action.get("type")
        start_time = action.get("start_time")
        end_time = action.get("end_time")
        action_suggestion = action.get("action_suggestion", action.get("action_taken", "no_specific_action")) # Use action_taken for profanity

        self._log(f"\n--- Applying Action [{action_type}] at {current_playback_time:.2f}s "
                  f"(Duration: {end_time-start_time:.2f}s) ---")

        if action_type == "profanity_mute":
            # Action suggestion from filters.json (mute_audio or replace_text)
            if action_suggestion == "mute_audio":
                # if self.player and vlc:
                #     self.player.audio_set_volume(0) # Mute audio
                # else:
                self._log(f"  [SIMULATED] Muting audio for profanity: '{action.get('matched_word')}'")
                # In real scenario, would schedule unmute after end_time
            elif action_suggestion == "replace_text":
                self._log(f"  [SIMULATED] Replacing subtitle text: '{action.get('original_text')}' -> '{action.get('action_taken')}'")
            else:
                 self._log(f"  [SIMULATED] Profanity detected, but specific action '{action_suggestion}' is not simulated for player.")
        elif action_type == "nudity_detection":
            if action_suggestion == "blur_region":
                self._log(f"  [SIMULATED] Applying blur effect for nudity from {start_time:.2f}s to {end_time:.2f}s.")
            elif action_suggestion == "skip_scene":
                self._log(f"  [SIMULATED] Skipping nudity scene from {start_time:.2f}s to {end_time:.2f}s. (Simulating jump)")
                # if self.player and vlc:
                #     self.player.set_time(int(end_time * 1000)) # Jump to end of scene
                # Update current_playback_time in simulation to skip ahead
                # This affects the simulation loop's current time directly.
                simulated_skip_duration = end_time - current_playback_time
                if simulated_skip_duration > 0:
                    global_start_time = time.time() - current_playback_time
                    time.sleep(simulated_skip_duration) # Simulate delay of skipping
                    # current_playback_time will be recalculated based on real elapsed time
            else:
                self._log(f"  [SIMULATED] Nudity detected, suggested action: {action_suggestion}")
        elif action_type == "violence_detection":
            if action_suggestion == "skip_scene":
                self._log(f"  [SIMULATED] Skipping violence scene from {start_time:.2f}s to {end_time:.2f}s. (Simulating jump)")
                simulated_skip_duration = end_time - current_playback_time
                if simulated_skip_duration > 0:
                    global_start_time = time.time() - current_playback_time
                    time.sleep(simulated_skip_duration)
            elif action_suggestion == "mute_audio":
                 self._log(f"  [SIMULATED] Muting audio for violence from {start_time:.2f}s to {end_time:.2f}s.")
            else:
                self._log(f"  [SIMULATED] Violence detected, suggested action: {action_suggestion}")
        else:
            self._log(f"  [SIMULATED] Unknown action type: {action_type}")
        self._log("-" * 50)


    def stop(self):
        """Stops media playback (simulated)."""
        # if self.player and vlc:
        #     self.player.stop()
        #     self.instance.release()
        #     self._log("VLC player stopped.")
        # else:
        self._log("Simulated player stopped.")


if __name__ == '__main__':
    # Example usage for testing this module
    dummy_video_file = 'movie/input/sample_movie.mp4' # Changed from your_movie.mp4 for consistency
    dummy_metadata_file = 'movie/metadata/sample_movie.json' # Changed from your_movie.json

    # Ensure directories exist
    os.makedirs('movie/input', exist_ok=True)
    os.makedirs('movie/metadata', exist_ok=True)
    os.makedirs('config', exist_ok=True)

    # Create a dummy video file if it doesn't exist
    if not os.path.exists(dummy_video_file):
        with open(dummy_video_file, 'w') as f:
            f.write("# This is a placeholder for a video file.")
        print(f"Created placeholder: {dummy_video_file}")

    # Create dummy metadata for testing player overlay
    dummy_metadata = {
        "media_file": "sample_movie.mp4",
        "processed_at": "2024-01-01 12:00:00",
        "filters_applied": {
            "profanity": True,
            "nudity": True,
            "violence": True
        },
        "actions": [
            {"type": "profanity_mute", "start_time": 5.0, "end_time": 6.5, "matched_word": "damn", "action_taken": "replaced 'damn' with '[bleep]'", "action_suggestion": "mute_audio"},
            {"type": "nudity_detection", "start_time": 10.0, "end_time": 15.0, "confidence": 0.85, "action_suggestion": "blur_region"},
            {"type": "profanity_mute", "start_time": 20.0, "end_time": 21.0, "matched_word": "shit", "action_taken": "replaced 'shit' with '[bleep]'", "action_suggestion": "replace_text"}, # Example for replace text action
            {"type": "violence_detection", "start_time": 25.0, "end_time": 30.0, "confidence": 0.9, "action_suggestion": "skip_scene"},
            {"type": "profanity_mute", "start_time": 30.5, "end_time": 31.5, "matched_word": "hell", "action_taken": "replaced 'hell' with '[bleep]'", "action_suggestion": "mute_audio"},
            {"type": "nudity_detection", "start_time": 40.0, "end_time": 42.0, "confidence": 0.78, "action_suggestion": "skip_scene"}, # Different action for nudity
            {"type": "violence_detection", "start_time": 55.0, "end_time": 58.0, "confidence": 0.75, "action_suggestion": "mute_audio"} # Different action for violence
        ]
    }
    with open(dummy_metadata_file, 'w', encoding='utf-8') as f:
        json.dump(dummy_metadata, f, indent=4)
    print(f"Created dummy metadata file: {dummy_metadata_file}")

    # Create dummy settings.yaml for testing (will be handled by config_manager init)
    # The config_manager will create default settings if they don't exist
    # No need to explicitly create dummy settings here if config_manager handles it.

    # Initialize and play
    controller = MediaPlaybackController(dummy_video_file, dummy_metadata_file)
    controller.play(log_callback=print) # Pass print as a simple log callback
    controller.stop()
