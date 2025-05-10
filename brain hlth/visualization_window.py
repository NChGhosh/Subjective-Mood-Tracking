import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import insights_generator
import matplotlib.pyplot as plt # Import matplotlib to close figures

class VisualizationWindow(ctk.CTkToplevel):
    """
    A top-level window to display the weekly mood sentiment visualization.
    Minimalist version with only the weekly plot, with a Back button.
    Ensures the correct method from InsightsGenerator is called.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("Weekly Mood Insights") # Updated title to Weekly
        # Adjusted size - might need further tuning based on screen resolution
        self.geometry("700x650") # Slightly increased height for the button
        self.transient(master)
        self.grab_set()

        self.insights_generator = insights_generator.InsightsGenerator()

        # --- Layout ---
        self.frame = ctk.CTkFrame(master=self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        # Configure grid within the main frame to manage controls and plot area
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=0) # Back button row
        self.frame.grid_rowconfigure(1, weight=1) # Plot area row


        # --- Back Button ---
        self.back_button = ctk.CTkButton(master=self.frame, text="Back", command=self.destroy)
        self.back_button.grid(row=0, column=0, pady=5, padx=10, sticky="w")


        # Frame to hold the Matplotlib Canvas widget
        self.plot_area_frame = ctk.CTkFrame(master=self.frame)
        self.plot_area_frame.grid(row=1, column=0, pady=10, padx=10, sticky="nsew") # Adjusted row
        self.plot_area_frame.grid_columnconfigure(0, weight=1) # Make the column expandable
        self.plot_area_frame.grid_rowconfigure(0, weight=1) # Make the plot row expandable


        # We will embed the FigureCanvasTkAgg widget directly into this frame
        self.sentiment_canvas_widget = None # To hold the Matplotlib canvas widget

        # --- Initial Plot Display ---
        self.update_plot() # Display the initial weekly plot


    def update_plot(self):
        """Generates and displays the weekly sentiment plot."""
        print("VisualizationWindow: Updating weekly sentiment plot.")

        # Clear previous plot and destroy old canvas widget
        if self.sentiment_canvas_widget:
            self.sentiment_canvas_widget.get_tk_widget().grid_forget()
            self.sentiment_canvas_widget.get_tk_widget().destroy()
            self.sentiment_canvas_widget = None

        # Generate the weekly sentiment plot (CALLING THE CORRECTED METHOD)
        sentiment_fig = self.insights_generator.generate_weekly_sentiment_plot() # CORRECTED METHOD CALL

        # Embed the sentiment plot on its dedicated grid cell
        self.sentiment_canvas_widget = FigureCanvasTkAgg(sentiment_fig, master=self.plot_area_frame)
        self.sentiment_canvas_widget.draw()
        # Use grid with sticky="nsew" to make it fill the cell
        self.sentiment_canvas_widget.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Close the Matplotlib figure to free up memory
        plt.close(sentiment_fig)

# Example usage (for testing independently - requires dummy subjective_data.csv with SentimentScore)
# if __name__ == "__main__":
#     ctk.set_appearance_mode("System")
#     ctk.set_default_color_theme("blue")
#
#     root = ctk.CTk()
#     root.geometry("200x100")
#     root.title("Main App")
#
#     # Ensure you have a dummy 'subjective_data.csv' file with the 'SentimentScore' column
#     # Refer to the example dummy data generation in insights_generator.py if needed.
#
#     def open_viz():
#          viz_window = VisualizationWindow(master=root)
#
#     button = ctk.CTkButton(master=root, text="Open Weekly Insights", command=open_viz)
#     button.pack(pady=20)
#
#     root.mainloop()
