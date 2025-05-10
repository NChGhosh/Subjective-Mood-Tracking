import customtkinter as ctk
import tkinter as tk
import colorsys # Module to convert RGB to HSB (HSV in Python)
import tkinter.messagebox # Import messagebox for error popups

class MoodInputWindow(ctk.CTkToplevel):
    """
    A top-level window for users to input their subjective mood
    by selecting a color and optionally providing text context.
    Now uses a simplified HSB-based approach to assign sentiment scores.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("How are you feeling?")
        self.geometry("450x600") # Increased size
        self.transient(master)
        self.grab_set()

        self.selected_color = None
        self.selected_emotion = None # We'll derive a simple emotion label from sentiment
        self.sentiment_score = None
        self.optional_text = ""

        # --- Color Palette (You can customize these colors) ---
        # Using a diverse set of colors to test the HSB mapping
        self.color_palette = [
            "#FF0000", "#FF4500", "#FFA500", "#FFD700", "#FFFF00", # Reds, Oranges, Yellows
            "#90EE90", "#32CD32", "#008000", "#006400", "#008080", # Greens, Teals
            "#ADD8E6", "#87CEFA", "#4682B4", "#1E90FF", "#0000CD", # Light Blues, Blues, Dark Blues
            "#9370DB", "#8A2BE2", "#9400D3", "#800080", "#4B0082", # Purples, Indigos
            "#FFFFFF", "#C0C0C0", "#808080", "#404040", "#000000"  # White, Grays, Black
        ]

        self.placeholder_text = "Optional explanation..." # Define placeholder text

        # --- Layout for the Color Grid ---
        self.color_buttons_frame = ctk.CTkFrame(master=self)
        self.color_buttons_frame.pack(pady=10, padx=10)

        cols = 5 # Number of columns in the grid
        rows = len(self.color_palette) // cols + (len(self.color_palette) % cols > 0) # Calculate rows needed

        for i in range(len(self.color_palette)):
            color = self.color_palette[i]
            row_index = i // cols
            col_index = i % cols

            button = ctk.CTkButton(
                master=self.color_buttons_frame,
                text="", # No text, just color
                fg_color=color, # Foreground color (the button color)
                hover_color=color, # Keep the color the same on hover for simplicity
                width=40, # Adjust size as needed
                height=40,
                command=lambda c=color: self.on_color_select(c) # Pass color to the command
            )
            button.grid(row=row_index, column=col_index, padx=5, pady=5) # Use grid layout

        # --- Display Selected Color (Optional, helpful for debugging) ---
        self.selected_color_label = ctk.CTkLabel(master=self, text="Selected Color: None", font=("", 14))
        self.selected_color_label.pack(pady=(10, 5), padx=10)

        # --- Display Derived Sentiment/Emotion ---
        self.sentiment_label = ctk.CTkLabel(master=self, text="Sentiment: None", font=("", 14))
        self.sentiment_label.pack(pady=(0, 10), padx=10)


        # --- Optional Text Input ---
        self.text_input_label = ctk.CTkLabel(master=self, text="Optional explanation:")
        self.text_input_label.pack(pady=(10, 0), padx=10)

        self.text_input_textbox = ctk.CTkTextbox(master=self, width=300, height=100)
        self.text_input_textbox.pack(pady=(0, 10), padx=10)

        # Insert initial placeholder text and set its color
        self.text_input_textbox.insert("0.0", self.placeholder_text)
        self.text_input_textbox.configure(text_color="gray") # Initial color for placeholder


        # Bind events for automatic placeholder handling
        self.text_input_textbox.bind("<FocusIn>", self.clear_placeholder)
        self.text_input_textbox.bind("<FocusOut>", self.restore_placeholder)


        # --- Action Buttons ---
        self.button_frame = ctk.CTkFrame(master=self)
        self.button_frame.pack(pady=10)

        done_button = ctk.CTkButton(master=self.button_frame, text="DONE", command=self.on_done)
        done_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(master=self.button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=10)


    def hex_to_hsb(self, hex_color):
        """Converts a hex color string to HSB (HSV in Python's colorsys)."""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert hex to RGB (0-255 range)
        rgb_255 = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Convert RGB (0-1 range) to HSV (HSB)
        # colorsys.rgb_to_hsv expects RGB values in the range [0, 1]
        rgb_01 = (rgb_255[0] / 255.0, rgb_255[1] / 255.0, rgb_255[2] / 255.0)
        h, s, v = colorsys.rgb_to_hsv(*rgb_01) # H, S, V are in the range [0, 1]
        # H is Hue (0-1, maps to 0-360 degrees), S is Saturation (0-1), V is Value (Brightness) (0-1)
        return h, s, v # Returning H, S, V (Brightness)


    def assign_sentiment_from_hsb(self, h, s, v):
        """
        Assigns a simplified sentiment score (+1, 0, -1) based on HSB values.
        This is a simplified mapping based on general color psychology principles
        and is not a direct implementation of a research-based PAD model.

        H (Hue): 0-1 (0=Red, 0.16=Yellow, 0.33=Green, 0.5=Cyan, 0.66=Blue, 0.83=Magenta, 1=Red)
        S (Saturation): 0-1 (0=Grayscale, 1=Pure color)
        V (Value/Brightness): 0-1 (0=Black, 1=Brightest)
        """
        sentiment = 0 # Default to neutral (0)
        emotion_label = "Neutral"

        # --- Simplified Logic based on HSB ---

        # High Saturation often indicates more intense emotions (positive or negative)
        # Low Saturation (closer to gray) can indicate muted emotions or neutrality
        # Low Value (closer to black) can indicate negative emotions or lack of energy
        # High Value (closer to white) can indicate lightness or positivity

        # Pure Grays (low saturation) often neutral or negative
        if s < 0.1: # If saturation is very low (close to grayscale)
             if v < 0.3: # Dark grays/black
                  sentiment = -1
                  emotion_label = "Low Energy / Negative"
             elif v > 0.7: # Light grays/white
                  sentiment = 0 # Can be neutral or calm depending on context, default to neutral
                  emotion_label = "Calm / Neutral"
             else: # Medium grays
                  sentiment = 0
                  emotion_label = "Neutral"
        else: # Saturated colors
             # Map Hue ranges to general sentiment associations (simplified)
             # Red/Orange/Yellow (Warm colors) - Can be positive (excitement) or negative (anger)
             if (h >= 0 and h < 0.1) or (h >= 0.9 and h <= 1): # Reds
                  if v > 0.6: # Brighter Reds
                       sentiment = 0 # Intense, could be positive or negative, default neutral
                       emotion_label = "Intense"
                  else: # Darker Reds
                       sentiment = -1
                       emotion_label = "Negative / Angry"
             elif h >= 0.1 and h < 0.2: # Oranges
                  if v > 0.5:
                       sentiment = +1
                       emotion_label = "Energetic / Positive"
                  else:
                       sentiment = 0
                       emotion_label = "Medium Energy"
             elif h >= 0.2 and h < 0.3: # Yellows
                  if v > 0.5:
                       sentiment = +1
                       emotion_label = "Happy / Cheerful"
                  else:
                       sentiment = 0
                       emotion_label = "Neutral / Muted"

             # Green/Cyan/Blue (Cool colors) - Can be positive (calm) or negative (sadness)
             elif h >= 0.3 and h < 0.5: # Greens/Cyans
                  if v > 0.4:
                       sentiment = +1
                       emotion_label = "Calm / Peaceful"
                  else:
                       sentiment = 0
                       emotion_label = "Muted Calm"
             elif h >= 0.5 and h < 0.7: # Blues
                  if v > 0.5: # Brighter Blues
                       sentiment = 0 # Can be calm or sad, default neutral
                       emotion_label = "Calm / Serene"
                  else: # Darker Blues
                       sentiment = -1
                       emotion_label = "Sad / Low Mood"

             # Magenta/Purple (Often complex associations)
             elif h >= 0.7 and h < 0.9: # Magentas/Purples
                  if s > 0.5 and v > 0.5:
                       sentiment = 0 # Can be creative, mysterious, or anxious - default neutral
                       emotion_label = "Complex / Introspective"
                  else:
                       sentiment = 0
                       emotion_label = "Muted / Neutral"

        # Ensure sentiment is one of the allowed values
        if sentiment not in [-1, 0, 1]:
             sentiment = 0 # Default to neutral if logic fails

        # Assign a simple emotion label based on the final sentiment score
        if sentiment == 1:
             emotion_label = "Positive"
        elif sentiment == -1:
             emotion_label = "Negative"
        else:
             emotion_label = "Neutral"


        return sentiment, emotion_label


    def on_color_select(self, color):
        """Handles a color button click - stores color, calculates HSB and sentiment, updates labels."""
        self.selected_color = color # Store the chosen color
        self.selected_color_label.configure(text=f"Selected Color: {self.selected_color}")

        # Calculate HSB
        h, s, v = self.hex_to_hsb(color)
        print(f"Selected Color: {color}, HSB: ({h:.2f}, {s:.2f}, {v:.2f})") # Debug print HSB

        # Assign sentiment and emotion based on HSB
        self.sentiment_score, self.selected_emotion = self.assign_sentiment_from_hsb(h, s, v)

        self.sentiment_label.configure(text=f"Sentiment: {self.selected_emotion} ({self.sentiment_score})")
        print(f"Derived Sentiment: {self.sentiment_score}, Emotion: {self.selected_emotion}") # Debug print sentiment


    def on_done(self):
        """Handles the DONE button click - captures text and closes window, ensures selection."""
        # Ensure a color has been selected, which means sentiment_score and selected_emotion should be set
        if self.selected_color is not None and self.sentiment_score is not None:
             # Get text from the textbox
             current_text = self.text_input_textbox.get("0.0", "end").strip()
             if current_text == self.placeholder_text: # If text is still the placeholder, save empty string
                  self.optional_text = ""
             else:
                  self.optional_text = current_text # Otherwise, save the entered text

             # Now self.selected_color, self.selected_emotion, self.sentiment_score, and self.optional_text
             # hold the user's input. The calling code in app.py will access these after wait_window.

             print(f"Optional text entered: '{self.optional_text}'") # For debugging
             self.destroy() # Close the window
        else:
             print("Please select a color before clicking DONE.") # Inform user if no color selected
             # Optional: Show a message box to the user
             tk.messagebox.showwarning("Selection Required", "Please select a color before clicking DONE.")


    def clear_placeholder(self, event):
        """Clears the placeholder text when the textbox gets focus."""
        if self.text_input_textbox.get("0.0", "end").strip() == self.placeholder_text:
            self.text_input_textbox.delete("0.0", "end")
            # Let CustomTkinter handle the default input color based on theme/mode


    def restore_placeholder(self, event):
        """Restores the placeholder text if the textbox loses focus and is empty."""
        if not self.text_input_textbox.get("0.0", "end").strip():
            self.text_input_textbox.insert("0.0", self.placeholder_text)
            # Set the text color back to the placeholder color
            self.text_input_textbox.configure(text_color="gray")


# Example usage (for testing independently):
# if __name__ == "__main__":
#     ctk.set_appearance_mode("System")
#     ctk.set_default_color_theme("blue")
#
#     root = ctk.CTk()
#     root.geometry("200x100")
#     root.title("Main App")
#
#     def open_mood():
#         mood_window = MoodInputWindow(master=root)
#         root.wait_window(mood_window)
#
#         # After the window is destroyed, access the attributes from the instance
#         # Note: You need to keep a reference to the window object created in this scope
#         # The App class example in app.py shows a better way to manage the window instance
#
#         # Example of accessing results (assuming the window instance is 'mood_window' after it closes)
#         if hasattr(mood_window, 'selected_color') and mood_window.selected_color is not None:
#              print(f"Main app received color: {mood_window.selected_color}")
#              print(f"Main app received emotion: {mood_window.selected_emotion}")
#              print(f"Main app received sentiment: {mood_window.sentiment_score}")
#              print(f"Main app received text: '{mood_window.optional_text}'")
#         else:
#              print("Mood window closed or no color selected.")
#
#     button = ctk.CTkButton(master=root, text="Open Mood Input", command=open_mood)
#     button.pack(pady=20)
#
#     root.mainloop()
