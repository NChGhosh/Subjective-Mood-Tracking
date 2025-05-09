import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    """
    Implements basic anomaly detection on time-series data using Isolation Forest.
    """
    def __init__(self, contamination='auto', random_state=42):
        """
        Initializes the Isolation Forest model.
        contamination: The proportion of outliers in the data set. 'auto' or a float between 0 and 0.5.
        random_state: Seed for reproducibility.
        """
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self._is_trained = False

    def train(self, data):
        """
        Trains the anomaly detection model on the provided data.
        Data should be a pandas DataFrame with numerical features.
        """
        if data.empty:
            print("Warning: Cannot train anomaly detector on empty data.")
            return

        # Isolation Forest expects numerical data.
        # Ensure data is numeric and handle potential NaNs.
        numeric_data = data.select_dtypes(include=np.number).dropna()

        if numeric_data.empty:
             print("Warning: No numeric data available for training.")
             return

        try:
            self.model.fit(numeric_data)
            self._is_trained = True
            print("Anomaly detector trained successfully.")
        except Exception as e:
            print(f"Error during anomaly detector training: {e}")
            self._is_trained = False


    def predict(self, data):
        """
        Predicts anomalies in new data.
        Returns a pandas Series where -1 indicates an anomaly and 1 indicates a normal point.
        Data should have the same structure as the training data.
        """
        if not self._is_trained:
            print("Warning: Anomaly detector is not trained. Cannot predict.")
            return pd.Series(1, index=data.index) # Return all normal if not trained

        if data.empty:
             print("Warning: Cannot predict on empty data.")
             return pd.Series([], index=[])

        # Ensure data is numeric and handle potential NaNs, matching training data columns
        numeric_data = data.select_dtypes(include=np.number)
        # Align columns with the data used for training
        training_columns = self.model.feature_names_in_
        numeric_data = numeric_data[training_columns].dropna() # Drop NaNs for prediction too

        if numeric_data.empty:
             print("Warning: No valid numeric data available for prediction after alignment/dropna.")
             return pd.Series(1, index=data.index) # Return all normal if no valid data

        try:
            predictions = self.model.predict(numeric_data)
            # Return predictions as a pandas Series with the original index
            return pd.Series(predictions, index=numeric_data.index)
        except Exception as e:
            print(f"Error during anomaly prediction: {e}")
            return pd.Series(1, index=data.index) # Return all normal on error

    def get_anomaly_scores(self, data):
        """
        Calculates anomaly scores for data. Lower scores indicate higher anomaly likelihood.
        Returns a pandas Series with anomaly scores.
        """
        if not self._is_trained:
            print("Warning: Anomaly detector is not trained. Cannot get scores.")
            return pd.Series(0, index=data.index) # Return 0 scores if not trained

        if data.empty:
             print("Warning: Cannot get scores on empty data.")
             return pd.Series([], index=[])

        # Ensure data is numeric and handle potential NaNs, matching training data columns
        numeric_data = data.select_dtypes(include=np.number)
        training_columns = self.model.feature_names_in_
        numeric_data = numeric_data[training_columns].dropna()

        if numeric_data.empty:
             print("Warning: No valid numeric data available for scoring after alignment/dropna.")
             return pd.Series(0, index=data.index) # Return 0 scores if no valid data

        try:
            scores = self.model.decision_function(numeric_data)
            # Return scores as a pandas Series with the original index
            return pd.Series(scores, index=numeric_data.index)
        except Exception as e:
            print(f"Error getting anomaly scores: {e}")
            return pd.Series(0, index=data.index) # Return 0 scores on error


# Example Usage (for testing independently):
# if __name__ == "__main__":
#     # Create some dummy time-series data with anomalies
#     data = {'Value1': np.random.randn(100),
#             'Value2': np.random.rand(100) * 10}
#     df = pd.DataFrame(data)
#     # Introduce some anomalies
#     df.iloc[10:12, 0] = 10 # Spike in Value1
#     df.iloc[50:53, 1] = 50 # Spike in Value2
#     df.iloc[80, :] = [-5, -5] # Low values
#
#     # Add a timestamp index
#     df['Timestamp'] = pd.date_range(start='2023-01-01', periods=100, freq='D')
#     df.set_index('Timestamp', inplace=True)
#
#     print("Original Data with Anomalies:")
#     print(df.head())
#     print("...")
#     print(df.tail())
#
#     # Initialize and train the detector
#     detector = AnomalyDetector(contamination=0.05) # Assume 5% anomalies
#     detector.train(df)
#
#     # Predict anomalies
#     predictions = detector.predict(df)
#     print("\nAnomaly Predictions (-1 is anomaly, 1 is normal):")
#     print(predictions.value_counts())
#     print("\nAnomalous timestamps:")
#     print(predictions[predictions == -1].index.tolist())
#
#     # Get anomaly scores
#     scores = detector.get_anomaly_scores(df)
#     print("\nAnomaly Scores (lower is more anomalous):")
#     print(scores.head())
#     print("...")
#     print(scores.tail())
#
#     # Plot data and highlight anomalies (requires matplotlib)
#     # import matplotlib.pyplot as plt
#     # fig, ax = plt.subplots(figsize=(10, 6))
#     # ax.plot(df.index, df['Value1'], label='Value1')
#     # ax.plot(df.index, df['Value2'], label='Value2')
#     #
#     # # Highlight anomalies
#     # anomalous_points = df[predictions == -1]
#     # ax.scatter(anomalous_points.index, anomalous_points['Value1'], color='red', label='Anomaly (Value1)')
#     # ax.scatter(anomalous_points.index, anomalous_points['Value2'], color='red', label='Anomaly (Value2)')
#     #
#     # ax.set_title("Data with Detected Anomalies")
#     # ax.set_xlabel("Timestamp")
#     # ax.set_ylabel("Value")
#     # ax.legend()
#     # plt.xticks(rotation=45, ha='right')
#     # plt.tight_layout()
#     # plt.show()
