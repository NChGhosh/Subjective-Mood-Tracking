import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # To embed plots in Tkinter/CustomTkinter
import data_manager # Import data manager
from datetime import datetime
import numpy as np
from anomaly_detector import AnomalyDetector # Import the anomaly detector

# Ensure Matplotlib uses the TkAgg backend for compatibility with Tkinter/CustomTkinter
plt.switch_backend('TkAgg')

class InsightsGenerator:
    """
    Handles data loading, aggregation, plotting, and basic anomaly integration.
    Now includes anomaly detection on aggregated data.
    """
    def __init__(self):
        print("InsightsGenerator: Initializing...")
        self.activity_data = data_manager.load_activity_data()
        self.subjective_data = data_manager.load_subjective_data()

        print(f"InsightsGenerator: Loaded activity_data (empty={self.activity_data.empty}):\n{self.activity_data.head()}")
        print(f"InsightsGenerator: Loaded subjective_data (empty={self.subjective_data.empty}):\n{self.subjective_data.head()}")


        # Convert Timestamp columns to datetime objects
        if not self.activity_data.empty:
            self.activity_data['Timestamp'] = pd.to_datetime(self.activity_data['Timestamp'])
            self.activity_data.set_index('Timestamp', inplace=True)
            print(f"InsightsGenerator: Processed activity_data index:\n{self.activity_data.head()}")

        if not self.subjective_data.empty:
            self.subjective_data['Timestamp'] = pd.to_datetime(self.subjective_data['Timestamp'])
            self.subjective_data.set_index('Timestamp', inplace=True)
            print(f"InsightsGenerator: Processed subjective_data index:\n{self.subjective_data.head()}")


        # Initialize the anomaly detector (adjust contamination as needed)
        self.anomaly_detector = AnomalyDetector(contamination='auto') # 'auto' lets the model decide proportion

        # Store detected anomalies
        self.anomalies = pd.Series(dtype=int) # To store anomaly predictions (-1 or 1)
        print("InsightsGenerator: Initialization complete.")


    def aggregate_data(self, timeframe='W'):
        """
        Aggregates activity and subjective data by the specified timeframe.
        timeframe options: 'W' (Weekly), 'M' (Monthly), 'Y' (Yearly)
        """
        print(f"InsightsGenerator: Aggregating data for timeframe: {timeframe}")
        aggregated_activity = pd.DataFrame()
        aggregated_subjective = pd.DataFrame()

        if not self.activity_data.empty:
            activity_counts = self.activity_data[self.activity_data['ActiveApp'] == 'Computer Active'].resample(timeframe).size().fillna(0)
            aggregated_activity = pd.DataFrame({'ActiveCount': activity_counts})
            print(f"InsightsGenerator: Aggregated activity_data (empty={aggregated_activity.empty}):\n{aggregated_activity.head()}")


        if not self.subjective_data.empty:
            # For subjective data, let's count the frequency of each emotion per interval
            aggregated_subjective = self.subjective_data.groupby(pd.Grouper(freq=timeframe))['Emotion'].value_counts().unstack(fill_value=0)
            print(f"InsightsGenerator: Aggregated subjective_data (emotion counts) (empty={aggregated_subjective.empty}):\n{aggregated_subjective.head()}")


            # *** Feature Engineering for AI: Add a numerical representation of mood ***
            # This is a simple example - you could map emotions to scores (-1 to 1, etc.)
            # For hackathon, let's just count the total number of subjective entries per period
            subjective_counts = self.subjective_data.resample(timeframe).size().fillna(0)
            aggregated_subjective['SubjectiveCount'] = subjective_counts
            print(f"InsightsGenerator: Aggregated subjective_data (with counts) (empty={aggregated_subjective.empty}):\n{aggregated_subjective.head()}")


        # Combine the aggregated data
        combined_aggregated = aggregated_activity.join(aggregated_subjective, how='outer').fillna(0)
        print(f"InsightsGenerator: Combined aggregated data (empty={combined_aggregated.empty}):\n{combined_aggregated.head()}")

        return combined_aggregated

    def run_anomaly_detection(self, timeframe='W'):
        """
        Aggregates data, trains the anomaly detector, and predicts anomalies.
        Stores the results in self.anomalies.
        """
        print(f"InsightsGenerator: Running anomaly detection for timeframe: {timeframe}")
        aggregated_data = self.aggregate_data(timeframe)

        if aggregated_data.empty:
            print("InsightsGenerator: No data to run anomaly detection on.")
            self.anomalies = pd.Series(dtype=int)
            return

        # Train the model on the aggregated data
        self.anomaly_detector.train(aggregated_data)

        # Predict anomalies on the aggregated data
        self.anomalies = self.anomaly_detector.predict(aggregated_data)
        print(f"InsightsGenerator: Anomaly detection run complete. Detected {len(self.anomalies[self.anomalies == -1])} anomalies.")
        print("InsightsGenerator: Anomalous periods:", self.anomalies[self.anomalies == -1].index.tolist())


    def generate_activity_plot(self, data, timeframe_label="Weekly"):
        """Generates a Matplotlib plot for activity data and highlights anomalies."""
        print(f"InsightsGenerator: Generating activity plot for {timeframe_label}. Data empty: {data.empty}")
        if data.empty or 'ActiveCount' not in data.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No activity data available", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"{timeframe_label} Activity Summary")
            print("InsightsGenerator: Generated empty activity plot.")
            return fig

        fig, ax = plt.subplots(figsize=(10, 4))
        line, = ax.plot(data.index, data['ActiveCount'], marker='o', label='Active Count')

        ax.set_title(f"{timeframe_label} Activity Count")
        ax.set_xlabel(f"{timeframe_label} Period")
        ax.set_ylabel("Active Count (Proxy for Usage)")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Highlight Anomalies on the plot
        if not self.anomalies.empty:
             anomalous_indices = self.anomalies[self.anomalies == -1].index
             anomalous_points = data.loc[data.index.intersection(anomalous_indices)]
             if not anomalous_points.empty:
                  ax.scatter(anomalous_points.index, anomalous_points['ActiveCount'], color='red', s=100, zorder=5, label='Anomaly')

        ax.legend()
        print("InsightsGenerator: Generated activity plot with data.")
        return fig

    def generate_emotion_plot(self, data, timeframe_label="Weekly"):
        """Generates a Matplotlib plot for emotion frequency data and highlights anomalies."""
        print(f"InsightsGenerator: Generating emotion plot for {timeframe_label}. Data empty: {data.empty}")
        if data.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No subjective data available", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"{timeframe_label} Emotion Frequency")
            print("InsightsGenerator: Generated empty emotion plot.")
            return fig

        plot_data = data.drop(columns=['SubjectiveCount'], errors='ignore')

        fig, ax = plt.subplots(figsize=(10, 6))
        plot_data.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title(f"{timeframe_label} Emotion Frequency")
        ax.set_xlabel(f"{timeframe_label} Period")
        ax.set_ylabel("Frequency")
        ax.legend(title="Emotion", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        print("InsightsGenerator: Generated emotion plot with data.")
        return fig

    def generate_plots(self, timeframe='W'):
        """Generates both activity and emotion plots for the given timeframe."""
        print(f"InsightsGenerator: generate_plots called for timeframe: {timeframe}")
        aggregated_data = self.aggregate_data(timeframe)
        timeframe_label = {'W': 'Weekly', 'M': 'Monthly', 'Y': 'Yearly'}.get(timeframe, 'Period')

        # Separate data for plotting
        activity_data = aggregated_data[['ActiveCount']] if 'ActiveCount' in aggregated_data.columns else pd.DataFrame()
        emotion_data = aggregated_data.drop(columns=['ActiveCount'], errors='ignore')

        activity_fig = self.generate_activity_plot(activity_data, timeframe_label)
        emotion_fig = self.generate_emotion_plot(emotion_data, timeframe_label)

        print("InsightsGenerator: generate_plots finished.")
        return activity_fig, emotion_fig

