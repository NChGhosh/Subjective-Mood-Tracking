import customtkinter as ctk
import tkinter as tk
import colorsys # Module to convert RGB to HSB (HSV in Python)
import tkinter.messagebox # Import messagebox for error popups

class MoodInputWindow(ctk.CTkToplevel):
    """
    A top-level window for users to input their subjective mood
    by selecting a color and optionally providing text context.
    Uses a simplified HSB-based approach to assign sentiment scores
    and now selects more specific emotion labels based on HSB.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("How are you feeling?")
        self.geometry("450x600") # Increased size
        self.transient(master)
        self.grab_set()

        self.selected_color = None
        self.selected_emotion = None # This will now hold the specific emotion label
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

        # --- Display Derived Emotion and Sentiment ---
        self.emotion_sentiment_label = ctk.CTkLabel(master=self, text="Emotion: None (Sentiment: None)", font=("", 14)) # Combined label
        self.emotion_sentiment_label.pack(pady=(0, 10), padx=10)


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


    def assign_sentiment_and_emotion_from_hsb(self, h, s, v):
        """
        Assigns a simplified sentiment score (+1, 0, -1) and a more specific
        emotion label based on HSB values and inspiration from the emotion grid.
        This is a simplified mapping for the prototype.
        """
        sentiment = 0 # Default to neutral (0)
        emotion_label = "Neutral" # Default emotion label

        # Convert Hue from 0-1 range to 0-360 degrees for easier mapping
        h_degrees = h * 360

        # --- Simplified Logic based on HSB and Emotion Grid Areas ---

        # Low Saturation (Grayscale/Muted) - Tend towards Neutral or Low Energy
        if s < 0.2: # Lowering saturation threshold slightly
            if v < 0.3: # Very dark grays/black
                sentiment = -1
                emotion_label = "Low Energy" # From grid concept
            elif v > 0.7: # Very light grays/white
                 sentiment = 0
                 emotion_label = "Calm" # From grid concept
            else: # Medium grays
                sentiment = 0
                emotion_label = "Apathetic" # From grid concept
        # Saturated Colors
        else:
            # High Brightness/Value - Tend towards Higher Energy/Pleasantness (top of grid)
            if v > 0.6:
                if (h_degrees >= 0 and h_degrees < 20) or (h_degrees >= 340 and h_degrees <= 360): # Reds
                     sentiment = 0 # Can be intense positive or negative
                     emotion_label = "Intense" # General high arousal
                elif h_degrees >= 20 and h_degrees < 75: # Orange to Yellow
                     sentiment = +1
                     emotion_label = "Excited" # Top right of grid
                elif h_degrees >= 75 and h_degrees < 155: # Green
                     sentiment = +1
                     emotion_label = "Lively" # Top right of grid
                elif h_degrees >= 155 and h_degrees < 240: # Blue
                     sentiment = +1
                     emotion_label = "Upbeat" # Top right of grid
                elif h_degrees >= 240 and h_degrees < 300: # Purple
                     sentiment = 0
                     emotion_label = "Surprised" # Top middle of grid
                elif h_degrees >= 300 and h_degrees < 340: # Pink
                     sentiment = +1
                     emotion_label = "Joyful" # High Pleasantness area
                else:
                     sentiment = 0
                     emotion_label = "Energetic" # Default for high value saturated
            # Medium Brightness/Value
            elif v > 0.3: # Above dark threshold but not very bright
                if (h_degrees >= 0 and h_degrees < 20) or (h_degrees >= 340 and h_degrees <= 360): # Reds
                     sentiment = -1
                     emotion_label = "Angry" # Top left of grid
                elif h_degrees >= 20 and h_degrees < 75: # Orange to Yellow
                     sentiment = +1
                     emotion_label = "Happy" # Middle right of grid
                elif h_degrees >= 75 and h_degrees < 155: # Green
                     sentiment = +1
                     emotion_label = "Content" # Middle right of grid
                elif h_degrees >= 155 and h_degrees < 240: # Blue
                     sentiment = 0 # Can be calm or sad
                     emotion_label = "Pleasant" # Middle of grid
                elif h_degrees >= 240 and h_degrees < 300: # Purple
                     sentiment = 0
                     emotion_label = "Introspective" # General association
                elif h_degrees >= 300 and h_degrees < 340: # Pink
                     sentiment = +1
                     emotion_label = "Hopeful" # Middle right area
                else:
                     sentiment = 0
                     emotion_label = "Neutral" # Fallback
            # Low Brightness/Value - Tend towards Lower Energy/Pleasantness (bottom of grid)
            else: # v <= 0.3 (but s > 0.2)
                 if (h_degrees >= 0 and h_degrees < 20) or (h_degrees >= 340 and h_degrees <= 360): # Dark Reds
                      sentiment = -1
                      emotion_label = "Enraged" # Top left corner (intense negative)
                 elif h_degrees >= 155 and h_degrees < 240: # Dark Blues
                      sentiment = -1
                      emotion_label = "Depressed" # Bottom left of grid
                 elif h_degrees >= 75 and h_degrees < 155: # Dark Greens
                      sentiment = 0 # Can be muted calm
                      emotion_label = "Restful" # Bottom right area
                 else:
                      sentiment = -1 # Default for dark saturated colors
                      emotion_label = "Low Mood" # General low pleasantness


        # Ensure sentiment is one of the allowed values (-1, 0, 1)
        # This is a safeguard, the logic above should primarily produce these
        if sentiment not in [-1, 0, 1]:
             sentiment = 0 # Default to neutral if logic somehow fails

        # Refine emotion label based on final sentiment if needed (optional)
        # This ensures the label broadly matches the sentiment score
        if sentiment == 1 and emotion_label in ["Angry", "Frustrated", "Depressed", "Sad", "Low Energy", "Low Mood", "Apathetic", "Intense", "Surprised"]:
             # If a positive sentiment was assigned but the label is typically negative/neutral, adjust label
             emotion_label = "Positive"
        elif sentiment == -1 and emotion_label in ["Excited", "Happy", "Content", "Peaceful", "Calm", "Lively", "Upbeat", "Joyful", "Hopeful", "Pleasant", "Restful"]:
             # If a negative sentiment was assigned but the label is typically positive/neutral, adjust label
             emotion_label = "Negative"
        elif sentiment == 0 and emotion_label in ["Excited", "Happy", "Content", "Peaceful", "Calm", "Lively", "Upbeat", "Joyful", "Hopeful", "Positive", "Negative", "Depressed", "Sad", "Angry", "Frustrated", "Enraged", "Low Mood"]:
             # If a neutral sentiment was assigned but the label is typically positive/negative, adjust label
             emotion_label = "Neutral"


        return sentiment, emotion_label


    def on_color_select(self, color):
        """Handles a color button click - stores color, calculates HSB and sentiment/emotion, updates labels."""
        self.selected_color = color # Store the chosen color
        self.selected_color_label.configure(text=f"Selected Color: {self.selected_color}")

        # Calculate HSB
        h, s, v = self.hex_to_hsb(color)
        print(f"Selected Color: {color}, HSB: ({h:.2f}, {s:.2f}, {v:.2f})") # Debug print HSB

        # Assign sentiment and emotion based on HSB
        self.sentiment_score, self.selected_emotion = self.assign_sentiment_and_emotion_from_hsb(h, s, v)

        # Update the label to show both emotion and sentiment
        self.emotion_sentiment_label.configure(text=f"Emotion: {self.selected_emotion} (Sentiment: {self.sentiment_score})")
        print(f"Derived Sentiment: {self.sentiment_score}, Emotion: {self.selected_emotion}") # Debug print sentiment


    def on_done(self):
        """Handles the DONE button click - captures text and closes window, ensures selection."""
        # Ensure a color has been selected, which means sentiment_score and selected_emotion should be set
        if self.selected_color is not None and self.sentiment_score is not None and self.selected_emotion is not None:
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
