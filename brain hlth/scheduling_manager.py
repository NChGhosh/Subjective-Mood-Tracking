import json
import os
import time
import threading
from datetime import datetime, timedelta, time as dt_time # Import time as dt_time

SCHEDULE_FILE = 'schedule_settings.json'

class Scheduler:
    """
    Manages scheduling of subjective input prompts.
    Runs in a background thread and triggers a callback in the main GUI thread.
    """
    def __init__(self, master_app):
        # Store a reference to the main application instance
        # We need this to call methods in the main GUI thread (using after)
        self.master_app = master_app
        self._is_running = False
        self._thread = None
        self.schedule = self.load_schedule()
        self._last_check_time = datetime.now() # Track last time checked

    def load_schedule(self):
        """Loads scheduling settings from a JSON file."""
        if os.path.isfile(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, 'r') as f:
                    schedule_data = json.load(f)
                    # Convert time string back to datetime.time object if stored as string
                    if 'time' in schedule_data and isinstance(schedule_data['time'], str):
                         # Use dt_time here as well
                         hour, minute = map(int, schedule_data['time'].split(':'))
                         schedule_data['time'] = dt_time(hour, minute)
                    return schedule_data
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading schedule file: {e}. Starting with empty schedule.")
                return {}
        return {}

    def save_schedule(self, schedule_data):
        """Saves scheduling settings to a JSON file."""
        # Convert time object to string for JSON serialization
        # Use dt_time here for the isinstance check
        if 'time' in schedule_data and isinstance(schedule_data['time'], dt_time):
             schedule_data['time'] = schedule_data['time'].strftime('%H:%M')

        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedule_data, f, indent=4)
        self.schedule = schedule_data # Update internal schedule
        print("Schedule saved.")

    def check_schedule(self):
        """Checks if a prompt is due based on the current time and schedule."""
        if not self.schedule or 'time' not in self.schedule or 'repeat_days' not in self.schedule:
            return False # No schedule set

        scheduled_time_obj = self.schedule['time']
        repeat_days = self.schedule['repeat_days'] # List of day names (e.g., ["Monday", "Wednesday"])

        now = datetime.now()
        current_day_name = now.strftime('%A') # Get current day name (e.g., "Wednesday")

        # Check if today is a scheduled day
        if current_day_name not in repeat_days:
            return False

        # Create a datetime object for the scheduled time today
        scheduled_datetime_today = now.replace(hour=scheduled_time_obj.hour, minute=scheduled_time_obj.minute, second=0, microsecond=0)

        # Check if the scheduled time is in the past and after the last check time
        # This prevents triggering multiple times for the same scheduled slot
        if now >= scheduled_datetime_today and self._last_check_time < scheduled_datetime_today:
             # Add a small buffer after the scheduled time to ensure it's truly passed
             if now < scheduled_datetime_today + timedelta(minutes=1): # Check within 1 minute after scheduled time
                  return True

        return False

    def schedule_loop(self):
        """The main loop for checking the schedule in the background."""
        while self._is_running:
            self._last_check_time = datetime.now() # Update last check time before sleeping
            if self.check_schedule():
                print("Scheduled time reached. Triggering mood input.")
                # *** Trigger the UI update in the main thread using after() ***
                # The after method takes a delay in milliseconds and a function to call.
                # We call a method in the master_app (the main App instance)
                self.master_app.after(0, self.master_app.open_mood_input) # Call open_mood_input immediately in main thread

            time.sleep(30) # Check schedule every 30 seconds (adjust as needed for responsiveness vs resource use)


    def start_scheduler(self):
        """Starts the background scheduling thread."""
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target=self.schedule_loop, daemon=True)
            self._thread.start()
            print("Scheduler started.")

    def stop_scheduler(self):
        """Stops the background scheduling thread."""
        if self._is_running:
            self._is_running = False
            if self._thread and self._thread.is_alive():
                self._thread.join()
            print("Scheduler stopped.")

# Example Usage (for testing the scheduler independently):
# if __name__ == "__main__":
#     # This requires a dummy master_app with an after method and open_mood_input
#     class DummyApp:
#         def after(self, delay, callback):
#             print(f"Dummy App: after({delay}, {callback.__name__}) called.")
#             callback() # Directly call for testing
#         def open_mood_input(self):
#             print("Dummy App: open_mood_input called.")
#
#     dummy_app = DummyApp()
#     scheduler = Scheduler(dummy_app)
#
#     # Example schedule data (replace with your test schedule)
#     test_schedule = {
#         'time': datetime.now().time().replace(second=0, microsecond=0), # Schedule for the current minute
#         'repeat_days': [datetime.now().strftime('%A')], # Schedule for today
#         'alarm_name': 'Test Prompt'
#     }
#     scheduler.save_schedule(test_schedule)
#
#     scheduler.start_scheduler()
#     try:
#         while True:
#             time.sleep(1) # Keep the main thread alive
#     except KeyboardInterrupt:
#         scheduler.stop_scheduler()
#         print("Scheduler stopped.")
