import customtkinter as ctk
import tkinter as tk
from datetime import datetime, time as dt_time
import scheduling_manager # Import the scheduler manager

class SchedulingWindow(ctk.CTkToplevel):
    """
    A top-level window for configuring subjective input scheduling.
    Allows setting time, repeat days, and alarm name.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Schedule Prompts")
        self.geometry("400x500") # Adjust size
        self.transient(master)
        self.grab_set()

        self.scheduler = scheduling_manager.Scheduler(master) # Use the scheduler manager
        self.current_schedule = self.scheduler.load_schedule() # Load existing schedule

        # --- Layout ---
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # --- Time Selection ---
        self.time_label = ctk.CTkLabel(master=self.frame, text="Schedule Time:")
        self.time_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Use Spinbox for hour and minute (CustomTkinter doesn't have built-in Spinbox, use Tkinter's)
        # Need to pack these into a sub-frame or use grid carefully
        self.time_frame = ctk.CTkFrame(master=self.frame)
        self.time_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Hour Spinbox (0-23 or 1-12) - Let's use 24-hour for simplicity in data
        self.hour_spinbox = tk.Spinbox(self.time_frame, from_=0, to=23, wrap=True, width=5, font=("", 12))
        self.hour_spinbox.pack(side="left", padx=5)

        self.colon_label = ctk.CTkLabel(master=self.time_frame, text=":", font=("", 12))
        self.colon_label.pack(side="left")

        # Minute Spinbox (0-59)
        self.minute_spinbox = tk.Spinbox(self.time_frame, from_=0, to=59, wrap=True, width=5, font=("", 12))
        self.minute_spinbox.pack(side="left", padx=5)

        # --- Alarm Name ---
        self.name_label = ctk.CTkLabel(master=self.frame, text="Alarm Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.name_entry = ctk.CTkEntry(master=self.frame, placeholder_text="e.g., Evening Check-in")
        self.name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- Repeat Days ---
        self.repeat_label = ctk.CTkLabel(master=self.frame, text="Repeat Weekly:")
        self.repeat_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

        self.days_frame = ctk.CTkFrame(master=self.frame)
        self.days_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.days_frame.grid_columnconfigure(0, weight=1) # Center the day buttons

        self.day_buttons = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days_of_week):
            # Use CTkButton as toggle buttons
            button = ctk.CTkButton(master=self.days_frame, text=day, width=100,
                                   fg_color="gray", hover_color="darkgray", # Default to off color
                                   command=lambda d=day: self.toggle_day(d))
            button.grid(row=i, column=0, pady=2, padx=5, sticky="ew")
            self.day_buttons[day] = button # Store button reference

        # --- Load existing settings ---
        self.load_settings()

        # --- Action Buttons ---
        self.button_frame = ctk.CTkFrame(master=self)
        self.button_frame.pack(pady=10)

        save_button = ctk.CTkButton(master=self.button_frame, text="SAVE", command=self.save_settings)
        save_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(master=self.button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=10)


    def load_settings(self):
        """Loads existing schedule settings into the UI elements."""
        if self.current_schedule:
            if 'time' in self.current_schedule and isinstance(self.current_schedule['time'], dt_time):
                 self.hour_spinbox.delete(0, "end")
                 self.hour_spinbox.insert(0, self.current_schedule['time'].hour)
                 self.minute_spinbox.delete(0, "end")
                 self.minute_spinbox.insert(0, self.current_schedule['time'].minute)

            if 'alarm_name' in self.current_schedule:
                 self.name_entry.delete(0, "end")
                 self.name_entry.insert(0, self.current_schedule['alarm_name'])

            if 'repeat_days' in self.current_schedule:
                 for day in self.current_schedule['repeat_days']:
                      if day in self.day_buttons:
                           self.day_buttons[day].configure(fg_color="blue", hover_color="darkblue") # Set to on color


    def toggle_day(self, day):
        """Toggles the selection of a repeat day."""
        if day in self.current_schedule.get('repeat_days', []):
            # Day is currently selected, deselect it
            self.current_schedule['repeat_days'].remove(day)
            self.day_buttons[day].configure(fg_color="gray", hover_color="darkgray")
        else:
            # Day is not selected, select it
            if 'repeat_days' not in self.current_schedule:
                 self.current_schedule['repeat_days'] = []
            self.current_schedule['repeat_days'].append(day)
            self.day_buttons[day].configure(fg_color="blue", hover_color="darkblue")

        print(f"Repeat days: {self.current_schedule.get('repeat_days', [])}") # For debugging


    def save_settings(self):
        """Collects settings from UI and saves them using the scheduler manager."""
        try:
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())
            scheduled_time = dt_time(hour, minute)
        except ValueError:
            print("Invalid time entered.")
            # You might want to show a message box here
            return

        alarm_name = self.name_entry.get().strip()
        repeat_days = self.current_schedule.get('repeat_days', []) # Get the toggled days

        new_schedule_data = {
            'time': scheduled_time,
            'repeat_days': repeat_days,
            'alarm_name': alarm_name
            # Add alarm tone here if implemented
        }

        self.scheduler.save_schedule(new_schedule_data)
        self.destroy() # Close the window after saving

# Example usage (for testing independently):
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("200x100")
#     root.title("Main App")
#
#     def open_schedule():
#          # Need a dummy scheduler instance for this test
#          class DummyScheduler:
#               def load_schedule(self): return {} # Or load test data
#               def save_schedule(self, data): print(f"Dummy Save: {data}")
#               def start_scheduler(self): pass
#               def stop_scheduler(self): pass
#          scheduler = DummyScheduler()
#          # Pass the dummy scheduler to the window
#          schedule_window = SchedulingWindow(master=root)
#          # You'll need to manually set the scheduler attribute for this test
#          schedule_window.scheduler = scheduler
#
#
#     button = ctk.CTkButton(master=root, text="Open Schedule", command=open_schedule)
#     button.pack(pady=20)
#
#     root.mainloop()
