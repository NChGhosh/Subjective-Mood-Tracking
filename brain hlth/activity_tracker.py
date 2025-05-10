import time
import threading
import psutil
import data_manager # Import the data manager module
from datetime import datetime

# You might need platform-specific imports here
# For Windows:
try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None
    win32process = None
    print("Warning: win32gui and win32process not found. Activity tracking may be limited on Windows.")


class ActivityTracker:
    def __init__(self):
        self._is_tracking = False
        self._thread = None
        self._sleep_interval = 10 # Original sleep interval
        self._check_interval = 0.1 # How often to check the stop flag during sleep


    def get_active_window_title(self):
        """Gets the title of the currently active window (Windows only, basic)."""
        if win32gui:
            try:
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            except:
                return "N/A" # Handle potential errors
        return "Tracking Not Available" # Placeholder for non-Windows or if import failed

    def get_active_process_name(self):
        """Gets the name of the process for the active window (more cross-platform with psutil)."""
        try:
            # This is a basic approach using psutil to list processes.
            # A more robust method would involve platform-specific calls
            # to get the foreground window's process ID.
            # For simplicity, let's just return a placeholder or a simple psutil check.
            # Example: Check if any process is using significant CPU (simplistic)
            # for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            #     try:
            #         if proc.info['cpu_percent'] > 5: # Arbitrary threshold
            #             return proc.info['name']
            #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            #         pass
            # return "Computer Active" # Default if no high CPU process found

            # A simpler approach: just indicate if the computer is idle or active based on input
            # This would require monitoring mouse/keyboard events, which adds complexity.
            # For now, let's stick to a basic process check or a placeholder.

            # Using get_active_window_title if available, otherwise a generic message
            window_title = self.get_active_window_title()
            if window_title and window_title != "Tracking Not Available":
                 return window_title
            else:
                 # Fallback or generic message
                 # You could add a simple check here like if total CPU usage is above a threshold
                 # if psutil.cpu_percent(interval=1) > 5: # Check CPU over 1 second
                 #      return "Computer Active"
                 # else:
                 #      return "Computer Idle"
                 return "Computer Activity" # Generic for simplicity


        except Exception as e:
            print(f"Error getting active process name: {e}")
            return "Tracking Error"


    def track_loop(self):
        """The main loop for activity tracking."""
        print("ActivityTracker: track_loop started.")
        while self._is_tracking:
            timestamp = datetime.now()
            active_info = self.get_active_process_name() # Using simplified check

            # In a real app, you'd process active_info to get meaningful app names
            # For hackathon, let's just save the active_info string
            data_manager.save_activity_data(timestamp, active_info)

            # --- Modified sleep mechanism for faster exit ---
            # Sleep for a short duration and check the flag repeatedly
            sleep_remaining = self._sleep_interval
            while sleep_remaining > 0 and self._is_tracking:
                sleep_duration = min(sleep_remaining, self._check_interval)
                time.sleep(sleep_duration)
                sleep_remaining -= sleep_duration
            # The loop exits quickly if _is_tracking becomes False


        print("ActivityTracker: track_loop finished.")


    def start_tracking(self):
        """Starts the activity tracking in a background thread."""
        if not self._is_tracking:
            self._is_tracking = True
            self._thread = threading.Thread(target=self.track_loop, daemon=True) # daemon=True allows thread to exit with main app
            self._thread.start()
            print("Activity tracking started.")

    def stop_tracking(self):
        """Stops the activity tracking thread."""
        if self._is_tracking:
            print("ActivityTracker: Stopping tracking thread.")
            self._is_tracking = False
            if self._thread and self._thread.is_alive():
                # Give the thread a moment to check the flag and exit the sleep loop
                self._thread.join(timeout=self._sleep_interval + 1) # Wait a bit longer than the max sleep
            print("ActivityTracker: Tracking stopped.")

# Example Usage (for testing the tracker independently):
# if __name__ == "__main__":
#     # Need a dummy data_manager with a save_activity_data method for this test
#     class DummyDataManager:
#          def save_activity_data(self, timestamp, active_info):
#               print(f"DummyDataManager: Saved activity: {active_info} at {timestamp}")
#
#     data_manager = DummyDataManager() # Use the dummy data manager
#
#     tracker = ActivityTracker()
#     tracker.start_tracking()
#     print("Tracker started. Press Ctrl+C to stop.")
#     try:
#         while True:
#             time.sleep(1) # Keep the main thread alive
#     except KeyboardInterrupt:
#         tracker.stop_tracking()
#         print("Tracker stopped by user.")
