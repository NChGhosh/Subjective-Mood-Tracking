import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # To embed plots in Tkinter/CustomTkinter
import data_manager # Import data manager
from datetime import datetime
import numpy as np
# from anomaly_detector import AnomalyDetector # AnomalyDetector is not needed for the minimalist AI


# Ensure Matplotlib uses the TkAgg backend for compatibility with Tkinter/CustomTkinter
plt.switch_backend('TkAgg')

class InsightsGenerator:
    """
    Handles data loading, weekly visualization, and the simple rule-based conclusion.
    """
    def __init__(self):
        print("InsightsGenerator: Initializing...")
        self.activity_data = data_manager.load_activity_data()
        self.subjective_data = data_manager.load_subjective_data()

        print(f"InsightsGenerator: Loaded activity_data (empty={self.activity_data.empty}):\n{self.activity_data.head()}")
        print(f"InsightsGenerator: Loaded subjective_data (empty={self.subjective_data.empty}):\n{self.subjective_data.head()}")

        # Convert Timestamp columns to datetime objects
        # These steps are generally fine, the issue was specifically with SentimentScore in older files
        if not self.activity_data.empty and 'Timestamp' in self.activity_data.columns:
            self.activity_data['Timestamp'] = pd.to_datetime(self.activity_data['Timestamp'], errors='coerce')
            self.activity_data.dropna(subset=['Timestamp'], inplace=True)
            # It's better to set index after potentially dropping NaNs
            if not self.activity_data.empty:
                self.activity_data.set_index('Timestamp', inplace=True)


        if not self.subjective_data.empty and 'Timestamp' in self.subjective_data.columns:
            self.subjective_data['Timestamp'] = pd.to_datetime(self.subjective_data['Timestamp'], errors='coerce')
            self.subjective_data.dropna(subset=['Timestamp'], inplace=True)
            # Ensure SentimentScore is numeric after loading/adding, before setting index
            if 'SentimentScore' in self.subjective_data.columns:
                 self.subjective_data['SentimentScore'] = pd.to_numeric(self.subjective_data['SentimentScore'], errors='coerce')
                 self.subjective_data.dropna(subset=['SentimentScore'], inplace=True) # Drop rows with NaN sentiment
            if not self.subjective_data.empty:
                self.subjective_data.set_index('Timestamp', inplace=True)


        # --- Simple AI Parameters ---
        self.min_submissions = 3
        self.threshold_happy = 0.5 # Example threshold for average sentiment
        self.threshold_bad = -0.5 # Example threshold for average sentiment

        print("InsightsGenerator: Initialization complete.")


    def get_simple_conclusion(self):
        """
        Applies the simple rule-based logic to generate a conclusion
        based on the average sentiment of recent subjective inputs.
        """
        print("InsightsGenerator: Generating simple conclusion.")
        # Ensure data is loaded and processed with sentiment score
        self.subjective_data = data_manager.load_subjective_data()
        if not self.subjective_data.empty and 'Timestamp' in self.subjective_data.columns:
            self.subjective_data['Timestamp'] = pd.to_datetime(self.subjective_data['Timestamp'], errors='coerce')
            self.subjective_data.dropna(subset=['Timestamp'], inplace=True)
            if 'SentimentScore' in self.subjective_data.columns:
                 self.subjective_data['SentimentScore'] = pd.to_numeric(self.subjective_data['SentimentScore'], errors='coerce')
                 self.subjective_data.dropna(subset=['SentimentScore'], inplace=True) # Drop rows with NaN sentiment
            if not self.subjective_data.empty:
                self.subjective_data.set_index('Timestamp', inplace=True)
        else:
             return "No subjective data yet."


        # For simplicity, let's consider the last N submissions
        # Use .copy() to avoid SettingWithCopyWarning
        recent_submissions = self.subjective_data.tail(self.min_submissions).copy()

        if len(recent_submissions) < self.min_submissions:
            return f"Need at least {self.min_submissions} mood entries for a conclusion."

        # --- Defensive check and conversion ---
        # This check might help diagnose if the column is truly missing at this point,
        # although the primary fix is ensuring the CSV file has the column correctly.
        if 'SentimentScore' not in recent_submissions.columns:
            print("Debug: 'SentimentScore' column not found in recent_submissions DataFrame!")
            # If this happens, it means the data loading didn't add the column correctly.
            # The most likely cause is a persistent old CSV file.
            return "Error: Sentiment data column missing."


        # SentimentScore is already ensured to be numeric and NaNs dropped in the loading section above
        # So the following lines should be safer now:
        average_sentiment = recent_submissions['SentimentScore'].mean()

        print(f"InsightsGenerator: Average sentiment of last {len(recent_submissions)} submissions: {average_sentiment:.2f}")

        # ... rest of the conclusion logic
        if average_sentiment >= self.threshold_happy:
            return "Great achievement! Your recent mood is positive."
        elif average_sentiment <= self.threshold_bad:
            return "You may need some time to relax. Your recent mood is low."
        else:
            return "Well balanced. Your recent mood is neutral."


    def generate_weekly_sentiment_plot(self):
        """Generates a Matplotlib plot for weekly sentiment trends."""
        print("InsightsGenerator: Generating weekly sentiment plot.")

        # Ensure data is loaded and processed with sentiment score
        self.subjective_data = data_manager.load_subjective_data()
        if not self.subjective_data.empty and 'Timestamp' in self.subjective_data.columns:
            self.subjective_data['Timestamp'] = pd.to_datetime(self.subjective_data['Timestamp'], errors='coerce')
            self.subjective_data.dropna(subset=['Timestamp'], inplace=True)
            if 'SentimentScore' in self.subjective_data.columns:
                 self.subjective_data['SentimentScore'] = pd.to_numeric(self.subjective_data['SentimentScore'], errors='coerce')
                 self.subjective_data.dropna(subset=['SentimentScore'], inplace=True) # Drop rows with NaN sentiment
            if not self.subjective_data.empty:
                self.subjective_data.set_index('Timestamp', inplace=True)
        else:
             fig, ax = plt.subplots()
             ax.text(0.5, 0.5, "No subjective data available for weekly plot", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
             ax.set_title("Weekly Mood Sentiment Trend")
             print("InsightsGenerator: Generated empty weekly sentiment plot.")
             return fig


        # Aggregate sentiment by week
        # SentimentScore is already ensured to be numeric by this point
        weekly_sentiment = self.subjective_data.resample('W')['SentimentScore'].mean().dropna() # Drop weeks with no data/NaNs

        if weekly_sentiment.empty:
             fig, ax = plt.subplots()
             ax.text(0.5, 0.5, "Not enough subjective data across weeks for plotting", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
             ax.set_title("Weekly Mood Sentiment Trend")
             print("InsightsGenerator: Generated empty weekly sentiment plot due to insufficient data across weeks.")
             return fig


        fig, ax = plt.subplots(figsize=(10, 4))
        # Use weekly_sentiment.index for the x-axis, which will be Timestamps at week end
        ax.plot(weekly_sentiment.index, weekly_sentiment.values, marker='o', linestyle='-')

        # --- CORRECTED TITLE HERE ---
        ax.set_title("Weekly Mood Sentiment Trend (Average)") # Corrected title
        ax.set_xlabel("Week") # Updated label
        ax.set_ylabel("Average Sentiment Score (+1 Happy, -1 Bad)")
        ax.grid(True)
        # Format x-axis to show week start dates nicely
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(plt.matplotlib.dates.WeekdayLocator(byweekday=plt.matplotlib.dates.MO)) # Locate at Mondays
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        print("InsightsGenerator: Generated weekly sentiment plot with data.")
        return fig
