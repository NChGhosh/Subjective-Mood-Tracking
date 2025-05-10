import pandas as pd
import os
from datetime import datetime

ACTIVITY_FILE = 'activity_data.csv'
SUBJECTIVE_FILE = 'subjective_data.csv'
SCHEDULE_FILE = 'schedule_settings.json' # Added for scheduling

def save_activity_data(timestamp, active_info):
    """Appends activity data to the activity CSV file."""
    # Ensure timestamp is in a consistent format, e.g., ISO
    if not isinstance(timestamp, str):
        timestamp = timestamp.isoformat()

    data = {'Timestamp': [timestamp], 'ActiveInfo': [active_info]} # Changed ActiveApp to ActiveInfo for clarity
    df = pd.DataFrame(data)
    if not os.path.isfile(ACTIVITY_FILE):
        df.to_csv(ACTIVITY_FILE, index=False)
    else:
        df.to_csv(ACTIVITY_FILE, mode='a', header=False, index=False)
    # print(f"Logged activity: {active_info} at {timestamp}") # Keep or remove print for debugging

# Modified to accept 'sentiment_score'
def save_subjective_data(timestamp, color_choice, emotion, sentiment_score, optional_text=""):
    """Appends subjective data (color, emotion, sentiment_score, text) to the subjective CSV file."""
    # Ensure timestamp is in a consistent format, e.g., ISO
    if not isinstance(timestamp, str):
        timestamp = timestamp.isoformat()

    data = {'Timestamp': [timestamp], 'ColorChoice': [color_choice], 'Emotion': [emotion], 'SentimentScore': [sentiment_score], 'OptionalText': [optional_text]} # Added SentimentScore
    df = pd.DataFrame(data)
    if not os.path.isfile(SUBJECTIVE_FILE):
        df.to_csv(SUBJECTIVE_FILE, index=False)
    else:
        df.to_csv(SUBJECTIVE_FILE, mode='a', header=False, index=False)
    # print(f"Logged subjective choice: {color_choice}, Emotion: {emotion}, Sentiment: {sentiment_score}, Text: '{optional_text}' at {timestamp}") # Keep or remove print for debugging

def load_subjective_data():
    """Loads all subjective data from the CSV file, ensuring correct columns and types."""
    if os.path.isfile(SUBJECTIVE_FILE):
        try:
            df = pd.read_csv(SUBJECTIVE_FILE)
            # Ensure required columns exist
            required_cols = ['Timestamp', 'ColorChoice', 'Emotion', 'SentimentScore', 'OptionalText']
            for col in required_cols:
                if col not in df.columns:
                    # Add missing columns with None, but specifically 0 for SentimentScore
                    if col == 'SentimentScore':
                        df[col] = 0 # Default sentiment to 0 if column is missing
                    else:
                        df[col] = None # Default other missing columns to None

            # Ensure Timestamp is datetime and handle potential errors
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df.dropna(subset=['Timestamp'], inplace=True) # Drop rows with invalid timestamps

            # Ensure SentimentScore is numeric after loading/adding
            # Use errors='coerce' to turn any non-numeric values into NaN
            df['SentimentScore'] = pd.to_numeric(df['SentimentScore'], errors='coerce')
            # Optional: Drop rows where sentiment score couldn't be converted to numeric
            # df.dropna(subset=['SentimentScore'], inplace=True)


            return df
        except pd.errors.EmptyDataError:
             # Return a DataFrame with all required columns if the file is empty
             return pd.DataFrame(columns=['Timestamp', 'ColorChoice', 'Emotion', 'SentimentScore', 'OptionalText'])
    # Return a DataFrame with all required columns if the file doesn't exist
    return pd.DataFrame(columns=['Timestamp', 'ColorChoice', 'Emotion', 'SentimentScore', 'OptionalText'])


def load_activity_data():
    """Loads all activity data from the CSV file."""
    if os.path.isfile(ACTIVITY_FILE):
        try:
            df = pd.read_csv(ACTIVITY_FILE)
            # Ensure Timestamp is datetime and handle potential errors
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df.dropna(subset=['Timestamp'], inplace=True) # Drop rows with invalid timestamps
            # Ensure 'ActiveInfo' column exists for older files
            if 'ActiveInfo' not in df.columns and 'ActiveApp' in df.columns:
                 df['ActiveInfo'] = df['ActiveApp'] # Rename if old column name exists
            elif 'ActiveInfo' not in df.columns:
                 df['ActiveInfo'] = None # Add if completely missing

            return df[['Timestamp', 'ActiveInfo']] # Return only expected columns
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['Timestamp', 'ActiveInfo']) # Return empty if file is empty
    return pd.DataFrame(columns=['Timestamp', 'ActiveInfo'])

# You can add more complex loading/filtering later if needed
