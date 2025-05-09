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
            # This is a bit more complex to reliably link foreground window to process cross-platform
            # For a hackathon, you might simplify and just list running processes
            # or rely on get_active_window_title if targeting Windows.
            # A simpler approach with psutil:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                # This part is tricky to get the *active* one easily cross-platform
                # For hackathon, let's stick to a basic approach or simulate
                pass # Placeholder
            # A more reliable but Windows-specific method might be needed, or simplify scope.

            # *** Hackathon Simplification: Let's just track that *some* activity is happening ***
            # You could check CPU usage or network activity with psutil as a proxy for general use.
            cpu_usage = psutil.cpu_percent(interval=1) # Check CPU usage over 1 second
            if cpu_usage > 5: # Arbitrary threshold for "active"
                 return "Computer Active"
            else:
                 return "Computer Idle"


        except Exception as e:
            print(f"Error getting active process: {e}")
            return "Error"


    def track_loop(self):
        """The main loop for tracking activity."""
        while self._is_tracking:
            timestamp = datetime.now().isoformat()
            # For hackathon, let's use the simplified activity check
            active_info = self.get_active_process_name() # Using simplified psutil check

            # In a real app, you'd process active_info to get meaningful app names
            # For hackathon, let's just save the active_info string
            data_manager.save_activity_data(timestamp, active_info)

            time.sleep(10) # Log activity every 10 seconds (adjust interval as needed)

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
            self._is_tracking = False
            if self._thread and self._thread.is_alive():
                self._thread.join() # Wait for the thread to finish
            print("Activity tracking stopped.")

# Example Usage (for testing the tracker independently):
# if __name__ == "__main__":
#     tracker = ActivityTracker()
#     tracker.start_tracking()
#     try:
#         while True:
#             time.sleep(1) # Keep the main thread alive
#     except KeyboardInterrupt:
#         tracker.stop_tracking()
#         print("Tracker stopped.")