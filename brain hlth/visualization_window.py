import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import insights_generator
import matplotlib.pyplot as plt # Import matplotlib to close figures

class VisualizationWindow(ctk.CTkToplevel):
    """
    A top-level window to display data visualizations (plots) and trigger anomaly detection.
    Improved layout for embedding Matplotlib plots using grid.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Data Insights and Visualizations")
        # Adjusted size - might need further tuning based on screen resolution
        self.geometry("900x800")
        self.transient(master)
        self.grab_set()

        self.insights_generator = insights_generator.InsightsGenerator()

        # --- Layout ---
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        # Configure grid within the main frame to manage controls and plot area
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=0) # Controls row
        self.frame.grid_rowconfigure(1, weight=1) # Plot area row


        # Controls Frame (for timeframe selection and analysis button)
        self.controls_frame = ctk.CTkFrame(master=self.frame)
        # Use grid for controls frame to center elements
        self.controls_frame.grid(row=0, column=0, pady=10)
        self.controls_frame.grid_columnconfigure(0, weight=0)
        self.controls_frame.grid_columnconfigure(1, weight=0)
        self.controls_frame.grid_columnconfigure(2, weight=0)


        self.timeframe_label = ctk.CTkLabel(master=self.controls_frame, text="Select Timeframe:")
        self.timeframe_label.grid(row=0, column=0, padx=5, sticky="w")

        self.timeframe_options = ["Weekly", "Monthly", "Yearly"]
        self.timeframe_variable = ctk.StringVar(value=self.timeframe_options[0]) # Default to Weekly

        self.timeframe_optionmenu = ctk.CTkOptionMenu(master=self.controls_frame,
                                                      values=self.timeframe_options,
                                                      variable=self.timeframe_variable,
                                                      command=self.update_plots)
        self.timeframe_optionmenu.grid(row=0, column=1, padx=5, sticky="ew")


        # Button to trigger anomaly detection
        self.analyze_button = ctk.CTkButton(master=self.controls_frame, text="Run Anomaly Detection", command=self.run_analysis)
        self.analyze_button.grid(row=0, column=2, padx=15, sticky="e") # Added padding


        # Frame to hold the Matplotlib Canvas widgets
        self.plot_area_frame = ctk.CTkFrame(master=self.frame)
        self.plot_area_frame.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        # Configure grid within the plot area frame to stack plots vertically
        self.plot_area_frame.grid_columnconfigure(0, weight=1) # Make the column expandable
        self.plot_area_frame.grid_rowconfigure(0, weight=1) # Make the activity plot row expandable
        self.plot_area_frame.grid_rowconfigure(1, weight=1) # Make the emotion plot row expandable


        # We will embed FigureCanvasTkAgg widgets directly into this frame
        self.activity_canvas_widget = None # To hold the Matplotlib canvas widget for activity
        self.emotion_canvas_widget = None # To hold the Matplotlib canvas widget for emotion


        # --- Initial Plot Display ---
        self.update_plots(self.timeframe_variable.get()) # Display initial plots


    def update_plots(self, selected_timeframe):
        """Generates and displays plots based on the selected timeframe."""
        timeframe_code = {'Weekly': 'W', 'Monthly': 'M', 'Yearly': 'Y'}.get(selected_timeframe, 'W')

        # Clear previous plots and destroy old canvas widgets
        if self.activity_canvas_widget:
            # Use grid_forget instead of pack_forget as we are using grid
            self.activity_canvas_widget.get_tk_widget().grid_forget()
            self.activity_canvas_widget.get_tk_widget().destroy()
            self.activity_canvas_widget = None

        if self.emotion_canvas_widget:
            # Use grid_forget instead of pack_forget as we are using grid
            self.emotion_canvas_widget.get_tk_widget().grid_forget()
            self.emotion_canvas_widget.get_tk_widget().destroy()
            self.emotion_canvas_widget = None


        # Generate new plots (InsightsGenerator now uses self.anomalies internally)
        activity_fig, emotion_fig = self.insights_generator.generate_plots(timeframe_code)

        # Embed the activity plot on its dedicated grid cell
        self.activity_canvas_widget = FigureCanvasTkAgg(activity_fig, master=self.plot_area_frame)
        self.activity_canvas_widget.draw()
        # Use grid with sticky="nsew" to make it fill the cell
        self.activity_canvas_widget.get_tk_widget().grid(row=0, column=0, sticky="nsew")


        # Embed the emotion plot on its dedicated grid cell
        self.emotion_canvas_widget = FigureCanvasTkAgg(emotion_fig, master=self.plot_area_frame)
        self.emotion_canvas_widget.draw()
        # Use grid with sticky="nsew" to make it fill the cell
        self.emotion_canvas_widget.get_tk_widget().grid(row=1, column=0, sticky="nsew")


        # Close the Matplotlib figures to free up memory
        plt.close(activity_fig)
        plt.close(emotion_fig)

    def run_analysis(self):
        """Triggers anomaly detection and updates plots."""
        selected_timeframe = self.timeframe_variable.get()
        timeframe_code = {'Weekly': 'W', 'Monthly': 'M', 'Yearly': 'Y'}.get(selected_timeframe, 'W')

        print(f"Running anomaly detection for {selected_timeframe} timeframe...")
        self.insights_generator.run_anomaly_detection(timeframe_code)
        print("Analysis complete. Updating visualizations.")

        # Refresh plots to show anomalies
        self.update_plots(selected_timeframe)

        # Optional: Add a message box or status label to indicate analysis is done
        # ctk.CTkMessageBox(title="Analysis Complete", message=f"Anomaly detection finished for {selected_timeframe} timeframe.")

# Example usage (for testing independently - requires dummy data files)
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("200x100")
#     root.title("Main App")
#
#     # Dummy data generation code (copy and run in a separate script once to create files)
#     # import pandas as pd
#     # from datetime import datetime, timedelta
#     # import random
#     # import numpy as np # Needed for anomaly data
#     # import insights_generator # Needed for emotion map
#     #
#     # # Dummy Activity Data
#     # activity_data = []
#     # start_time = datetime.now() - timedelta(days=400) # Extend time for yearly view
#     # for i in range(400 * 10): # Log every ~2.4 minutes
#     #      timestamp = start_time + timedelta(minutes=i*2.4)
#     #      activity = "Computer Active" if random.random() > 0.2 else "Computer Idle" # 80% active
#     #      activity_data.append({'Timestamp': timestamp, 'ActiveApp': activity})
#     # # Introduce a period of unusually high activity
#     # for i in range(10):
#     #      timestamp = start_time + timedelta(days=300) + timedelta(minutes=i*5)
#     #      activity_data.append({'Timestamp': timestamp, 'ActiveApp': "Computer Active"}) # More active logs in a short period
#     #
#     # pd.DataFrame(activity_data).to_csv('activity_data.csv', index=False)
#     #
#     # # Dummy Subjective Data
#     # emotions = list(insights_generator.InsightsGenerator().color_emotion_map.values())
#     # subjective_data = []
#     # for i in range(150): # 150 entries
#     #      timestamp = start_time + timedelta(days=random.randint(0, 399), hours=random.randint(8, 22))
#     #      color = random.choice(list(insights_generator.InsightsGenerator().color_emotion_map.keys()))
#     #      emotion = insights_generator.InsightsGenerator().color_emotion_map[color]
#     #      subjective_data.append({'Timestamp': timestamp, 'ColorChoice': color, 'Emotion': emotion, 'OptionalText': f"Feeling {emotion}"})
#     # # Introduce a period of unusual emotion (e.g., many 'Angry' entries close together)
#     # for i in range(5):
#     #      timestamp = start_time + timedelta(days=310) + timedelta(hours=i)
#     #      subjective_data.append({'Timestamp': timestamp, 'ColorChoice': '#FF0000', 'Emotion': 'Angry', 'OptionalText': 'Very upset'})
#     #
#     # pd.DataFrame(subjective_data).to_csv('subjective_data.csv', index=False)
#
#
#     def open_viz():
#          viz_window = VisualizationWindow(master=root)
#
#     button = ctk.CTkButton(master=root, text="Open Visualizations", command=open_viz)
#     button.pack(pady=20)
#
#     root.mainloop()
