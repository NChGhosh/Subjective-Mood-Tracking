import pandas as pd
import os

ACTIVITY_FILE = 'activity_data.csv'
SUBJECTIVE_FILE = 'subjective_data.csv'
SCHEDULE_FILE = 'schedule_settings.json' # Added for scheduling

def save_activity_data(timestamp, active_app):
    """Appends activity data to the activity CSV file."""
    data = {'Timestamp': [timestamp], 'ActiveApp': [active_app]}
    df = pd.DataFrame(data)
    if not os.path.isfile(ACTIVITY_FILE):
        df.to_csv(ACTIVITY_FILE, index=False)
    else:
        df.to_csv(ACTIVITY_FILE, mode='a', header=False, index=False)
    # print(f"Logged activity: {active_app} at {timestamp}") # Keep or remove print for debugging

# Modified to accept 'emotion'
def save_subjective_data(timestamp, color_choice, emotion, optional_text=""):
    """Appends subjective data (color, emotion, text) to the subjective CSV file."""
    data = {'Timestamp': [timestamp], 'ColorChoice': [color_choice], 'Emotion': [emotion], 'OptionalText': [optional_text]}
    df = pd.DataFrame(data)
    if not os.path.isfile(SUBJECTIVE_FILE):
        df.to_csv(SUBJECTIVE_FILE, index=False)
    else:
        df.to_csv(SUBJECTIVE_FILE, mode='a', header=False, index=False)
    # print(f"Logged subjective choice: {color_choice}, Emotion: {emotion}, Text: '{optional_text}' at {timestamp}") # Keep or remove print for debugging

def load_activity_data():
    """Loads all activity data from the CSV file."""
    if os.path.isfile(ACTIVITY_FILE):
        return pd.read_csv(ACTIVITY_FILE)
    return pd.DataFrame(columns=['Timestamp', 'ActiveApp'])

def load_subjective_data():
    """Loads all subjective data from the CSV file."""
    if os.path.isfile(SUBJECTIVE_FILE):
        # Ensure 'Emotion' column exists for older files
        df = pd.read_csv(SUBJECTIVE_FILE)
        if 'Emotion' not in df.columns:
             df['Emotion'] = '' # Add empty column if missing
        return df
    return pd.DataFrame(columns=['Timestamp', 'ColorChoice', 'Emotion', 'OptionalText']) # Added Emotion column

# You can add more complex loading/filtering later if needed
