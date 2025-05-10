import customtkinter as ctk
import tkinter as tk
import threading
import time
from activity_tracker import ActivityTracker
from mood_input_window import MoodInputWindow
# Removed import for SchedulingWindow
# Removed import for Scheduler
import data_manager
from datetime import datetime

# Import InsightsGenerator to get the simple conclusion
from insights_generator import InsightsGenerator
from visualization_window import VisualizationWindow # Import the visualization window


# Set the appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """
    The main application class for the Mental Well-being Insights tool (Minimalist Scope).
    Manages the main window, activity tracker, subjective input flow,
    simple conclusion display, and weekly visualization.
    Scheduling functionality has been entirely removed.
    """
    def __init__(self):
        super().__init__()

        # --- Main Window Configuration ---
        self.title("Minimalist Well-being Insights") # Updated title
        self.geometry("600x450") # Adjusted height after removing scheduling button
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Status
        self.grid_rowconfigure(1, weight=0) # Buttons frame
        self.grid_rowconfigure(2, weight=1) # Conclusion display
        self.grid_rowconfigure(3, weight=0) # Exit button row

        # --- Initialize Components ---
        self.tracker = ActivityTracker()
        self.mood_window = None
        # Removed self.scheduling_window
        self.visualization_window = None

        # Removed Scheduler initialization and start
        # self.scheduler = Scheduler(master_app=self)
        # self.scheduler.start_scheduler()

        self.insights_generator = InsightsGenerator() # Initialize insights generator for conclusion


        # --- UI Layout ---
        self.status_label = ctk.CTkLabel(master=self, text="App Running. Tracking Activity...")
        self.status_label.grid(row=0, column=0, pady=10, padx=10)

        self.buttons_frame = ctk.CTkFrame(master=self)
        self.buttons_frame.grid(row=1, column=0, pady=10, padx=20)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        # Only two columns needed now after removing scheduling button
        # self.buttons_frame.grid_columnconfigure(2, weight=1)


        self.mood_button = ctk.CTkButton(master=self.buttons_frame, text="How are you feeling?", command=self.open_mood_input)
        self.mood_button.grid(row=0, column=0, pady=10, padx=10) # Adjusted column

        # Removed the schedule button
        # self.schedule_button = ctk.CTkButton(master=self.buttons_frame, text="Set Prompt Interval", command=self.open_scheduling_window)
        # self.schedule_button.grid(row=0, column=1, pady=10, padx=10)

        self.viz_button = ctk.CTkButton(master=self.buttons_frame, text="View Weekly Insights", command=self.open_visualization_window) # Updated text
        self.viz_button.grid(row=0, column=1, pady=10, padx=10) # Adjusted column to fill the space


        # --- Conclusion Display ---
        self.conclusion_label = ctk.CTkLabel(master=self, text="Conclusion: Loading...", font=("", 16, "bold"), wraplength=550)
        self.conclusion_label.grid(row=2, column=0, pady=20, padx=20, sticky="nsew")
        self.update_conclusion_display() # Display initial conclusion on startup


        # --- Exit Button ---
        self.exit_button = ctk.CTkButton(master=self, text="Exit", command=self.on_closing, fg_color="red", hover_color="darkred")
        self.exit_button.grid(row=3, column=0, pady=10, padx=20) # Placed in a new row


        # --- Start Tracking on App Initialization ---
        self.tracker.start_tracking()

        # --- Handle App Closing ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def open_mood_input(self):
        """
        Opens the subjective mood input window.
        Ensures only one mood input window can be open at a time.
        Waits for the window to close and processes the input, including sentiment score.
        Called manually.
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
             # Access attributes from the mood_window instance after wait_window returns
             if hasattr(self.mood_window, 'selected_color') and self.mood_window.selected_color is not None and \
                hasattr(self.mood_window, 'selected_emotion') and self.mood_window.selected_emotion is not None and \
                hasattr(self.mood_window, 'sentiment_score') and self.mood_window.sentiment_score is not None: # Check for sentiment

                  selected_color = self.mood_window.selected_color
                  selected_emotion = self.mood_window.selected_emotion
                  sentiment_score = self.mood_window.sentiment_score # Get the sentiment score
                  optional_text = getattr(self.mood_window, 'optional_text', "")
                  timestamp = datetime.now()

                  data_manager.save_subjective_data(timestamp, selected_color, selected_emotion, sentiment_score, optional_text) # Save sentiment
                  print(f"Mood input received and saved: Color={selected_color}, Emotion={selected_emotion}, Sentiment={sentiment_score}, Text='{optional_text}'")

                  # --- Update Conclusion After Saving ---
                  self.update_conclusion_display()
                  # Removed call to scheduler.update_last_prompt_time()


             else:
                  print("Mood input window closed without selection or incomplete input.")

        else:
            self.mood_window.lift()

    # Removed open_scheduling_window method

    def open_visualization_window(self):
        """
        Opens the data visualization window (weekly plot).
        Ensures only one visualization window can be open at a time.
        """
        if self.visualization_window is None or not self.visualization_window.winfo_exists():
            # Pass the insights generator to the visualization window
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

    def update_conclusion_display(self):
        """Loads data and updates the conclusion label based on the simple AI logic."""
        print("App: Updating conclusion display.")
        # Reload data in insights generator to get the latest subjective data
        # (This might be inefficient for a real app, but fine for a hackathon prototype)
        self.insights_generator = InsightsGenerator()
        conclusion = self.insights_generator.get_simple_conclusion()
        self.conclusion_label.configure(text=f"Conclusion: {conclusion}")
        print(f"App: Conclusion updated to: {conclusion}")


    def on_closing(self):
        """
        Handles actions to perform when the main application window is closed.
        Stops the background tracker before closing the GUI.
        """
        print("Closing application. Stopping tracker.")
        self.tracker.stop_tracking()
        # Removed call to scheduler.stop_scheduler()
        self.destroy()

# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
