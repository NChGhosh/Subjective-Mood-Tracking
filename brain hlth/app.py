import customtkinter as ctk
import tkinter as tk
import threading
import time
from activity_tracker import ActivityTracker
from mood_input_window import MoodInputWindow
from scheduling_window import SchedulingWindow
from scheduling_manager import Scheduler
from visualization_window import VisualizationWindow # Import the visualization window
import data_manager
from datetime import datetime

# Set the appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """
    The main application class for the Mental Well-being Insights tool.
    Manages the main window, activity tracker, subjective input flow, scheduling, and visualizations.
    """
    def __init__(self):
        super().__init__()

        # --- Main Window Configuration ---
        self.title("Mental Well-being Insights")
        self.geometry("600x450") # Slightly increased height
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Initialize Components ---
        self.tracker = ActivityTracker()
        self.mood_window = None
        self.scheduling_window = None
        self.visualization_window = None # Keep track of the visualization window

        self.scheduler = Scheduler(master_app=self)
        self.scheduler.start_scheduler()


        # --- UI Layout ---
        self.main_frame = ctk.CTkFrame(master=self)
        self.main_frame.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=0) # Added row for visualization button


        self.status_label = ctk.CTkLabel(master=self.main_frame, text="App Running. Tracking Activity...")
        self.status_label.grid(row=0, column=0, pady=10, padx=10)

        self.mood_button = ctk.CTkButton(master=self.main_frame, text="How are you feeling?", command=self.open_mood_input)
        self.mood_button.grid(row=1, column=0, pady=10, padx=10)

        self.schedule_button = ctk.CTkButton(master=self.main_frame, text="Schedule Prompts", command=self.open_scheduling_window)
        self.schedule_button.grid(row=2, column=0, pady=10, padx=10)

        # Button to open the visualization window
        self.viz_button = ctk.CTkButton(master=self.main_frame, text="View Insights", command=self.open_visualization_window)
        self.viz_button.grid(row=3, column=0, pady=10, padx=10)


        # --- Start Tracking on App Initialization ---
        self.tracker.start_tracking()

        # --- Handle App Closing ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def open_mood_input(self):
        """
        Opens the subjective mood input window.
        Ensures only one mood input window can be open at a time.
        Waits for the window to close and processes the input, including emotion.
        Called manually or by the scheduler.
        """
        if self.mood_window is None or not self.mood_window.winfo_exists():
             self.mood_window = MoodInputWindow(master=self)

             # --- Position the new window relative to the main window (Optional but good UX) ---
             self.mood_window.update()
             main_window_x = self.winfo_x()
             main_window_y = self.winfo_y()
             main_window_width = self.winfo_width()
             main_window_height = self.winfo_height()

             mood_window_width = self.mood_window.winfo_width()
             mood_window_height = self.mood_window.winfo_height()

             new_x = main_window_x + (main_window_width // 2) - (mood_window_width // 2)
             new_y = main_window_y + (main_window_height // 2) - (mood_window_height // 2)

             self.mood_window.geometry(f"+{new_x}+{new_y}")

             # --- Wait for the mood window to close and get the result ---
             self.wait_window(self.mood_window)

             # --- Process Data After Mood Window Closes ---
             if hasattr(self.mood_window, 'selected_color') and self.mood_window.selected_color is not None and \
                hasattr(self.mood_window, 'selected_emotion') and self.mood_window.selected_emotion is not None:

                  selected_color = self.mood_window.selected_color
                  selected_emotion = self.mood_window.selected_emotion
                  optional_text = getattr(self.mood_window, 'optional_text', "")
                  timestamp = datetime.now().isoformat()

                  data_manager.save_subjective_data(timestamp, selected_color, selected_emotion, optional_text)
                  print(f"Mood input received and saved: Color={selected_color}, Emotion={selected_emotion}, Text='{optional_text}'")
             else:
                  print("Mood input window closed without selection or incomplete input.")

        else:
            self.mood_window.lift()

    def open_scheduling_window(self):
        """
        Opens the scheduling settings window.
        Ensures only one scheduling window can be open at a time.
        """
        if self.scheduling_window is None or not self.scheduling_window.winfo_exists():
            self.scheduling_window = SchedulingWindow(master=self)
            # Position the new window (optional)
            self.scheduling_window.update()
            main_window_x = self.winfo_x()
            main_window_y = self.winfo_y()
            main_window_width = self.winfo_width()
            main_window_height = self.winfo_height()

            schedule_window_width = self.scheduling_window.winfo_width()
            schedule_window_height = self.scheduling_window.winfo_height()

            new_x = main_window_x + (main_window_width // 2) - (schedule_window_width // 2)
            new_y = main_window_y + (main_window_height // 2) - (schedule_window_height // 2)

            self.scheduling_window.geometry(f"+{new_x}+{new_y}")

        else:
            self.scheduling_window.lift()

    def open_visualization_window(self):
        """
        Opens the data visualization window.
        Ensures only one visualization window can be open at a time.
        """
        if self.visualization_window is None or not self.visualization_window.winfo_exists():
            self.visualization_window = VisualizationWindow(master=self)
            # Position the new window (optional)
            self.visualization_window.update()
            main_window_x = self.winfo_x()
            main_window_y = self.winfo_y()
            main_window_width = self.winfo_width()
            main_window_height = self.winfo_height()

            viz_window_width = self.visualization_window.winfo_width()
            viz_window_height = self.visualization_window.winfo_height()

            new_x = main_window_x + (main_window_width // 2) - (viz_window_width // 2)
            new_y = main_window_y + (main_window_height // 2) - (viz_window_height // 2)

            self.visualization_window.geometry(f"+{new_x}+{new_y}")
        else:
            self.visualization_window.lift()


    def on_closing(self):
        """
        Handles actions to perform when the main application window is closed.
        Stops the background tracker and scheduler before closing the GUI.
        """
        print("Closing application. Stopping tracker and scheduler.")
        self.tracker.stop_tracking()
        self.scheduler.stop_scheduler()
        self.destroy()

# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
