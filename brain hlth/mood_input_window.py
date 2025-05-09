import customtkinter as ctk
import tkinter as tk

class MoodInputWindow(ctk.CTkToplevel):
    """
    A top-level window for users to input their subjective mood
    by selecting a color and optionally providing text context.
    Now includes emotion labels associated with colors and automatic
    placeholder text handling in the text box with correct text color.
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.title("How are you feeling?")
        self.geometry("450x600") # Increased size
        self.transient(master)
        self.grab_set()

        self.selected_color = None
        self.selected_emotion = None
        self.optional_text = ""

        # --- Color-Emotion Mapping ---
        self.color_emotion_map = {
            # Reds/Oranges (High Energy, Intensity)
            "#FF0000": "Angry", "#FF4500": "Frustrated", "#FFA500": "Energetic", "#FFD700": "Excited", "#FFFF00": "Happy",
            # Greens/Teals (Calm, Growth, Balance)
            "#90EE90": "Calm", "#32CD32": "Hopeful", "#008000": "Content", "#006400": "Peaceful", "#008080": "Balanced",
            # Blues (Calm, Sadness, Serenity)
            "#ADD8E6": "Relaxed", "#87CEFA": "Serene", "#4682B4": "Neutral", "#1E90FF": "Sad", "#0000CD": "Depressed",
            # Purples/Indigos (Creativity, Mystery, Anxiety)
            "#9370DB": "Creative", "#8A2BE2": "Anxious", "#9400D3": "Confused", "#800080": "Mysterious", "#4B0082": "Introspective"
        }
        self.placeholder_text = "Optional explanation..." # Define placeholder text

        # --- Layout for the Color Grid ---
        self.color_buttons_frame = ctk.CTkFrame(master=self)
        self.color_buttons_frame.pack(pady=10, padx=10)

        colors = list(self.color_emotion_map.keys())
        cols = 5 # Number of columns in the grid
        rows = len(colors) // cols + (len(colors) % cols > 0) # Calculate rows needed

        for i in range(len(colors)):
            color = colors[i]
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

        # --- Display Selected Emotion ---
        self.selected_emotion_label = ctk.CTkLabel(master=self, text="Selected Emotion: None", font=("", 14))
        self.selected_emotion_label.pack(pady=(10, 5), padx=10)


        # --- Optional Text Input ---
        self.text_input_label = ctk.CTkLabel(master=self, text="I'm feeling this way because:")
        self.text_input_label.pack(pady=(10, 0), padx=10)

        self.text_input_textbox = ctk.CTkTextbox(master=self, width=300, height=100) # Adjusted size
        self.text_input_textbox.pack(pady=(0, 10), padx=10)

        # Insert initial placeholder text and set its color
        self.text_input_textbox.insert("0.0", self.placeholder_text)
        self.text_input_textbox.configure(text_color="gray") # Set placeholder text color

        # Set the default text color for user input to white
        self.text_input_textbox.configure(text_color="white") # Set default text color to white

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


    def on_color_select(self, color):
        """Handles a color button click - stores color and updates emotion label."""
        self.selected_color = color # Store the chosen color
        self.selected_emotion = self.color_emotion_map.get(color, "Unknown") # Get emotion from map
        self.selected_emotion_label.configure(text=f"Selected Emotion: {self.selected_emotion}")
        print(f"Color selected: {color}, Emotion: {self.selected_emotion}") # For debugging


    def on_done(self):
        """Handles the DONE button click - captures text and closes window."""
        if self.selected_color and self.selected_emotion: # Ensure both color and emotion are selected
             # Get text from the textbox
             current_text = self.text_input_textbox.get("0.0", "end").strip()
             if current_text == self.placeholder_text: # If text is still the placeholder, save empty string
                  self.optional_text = ""
             else:
                  self.optional_text = current_text # Otherwise, save the entered text


             print(f"Optional text entered: '{self.optional_text}'") # For debugging
             self.destroy() # Close the window
        else:
             print("Please select a color before clicking DONE.") # Inform user if no color/emotion selected

    def clear_placeholder(self, event):
        """Clears the placeholder text when the textbox gets focus."""
        if self.text_input_textbox.get("0.0", "end").strip() == self.placeholder_text:
            self.text_input_textbox.delete("0.0", "end")
            # When clearing, set the text color to the desired input color (white)
            self.text_input_textbox.configure(text_color="white")


    def restore_placeholder(self, event):
        """Restores the placeholder text if the textbox loses focus and is empty."""
        if not self.text_input_textbox.get("0.0", "end").strip():
            self.text_input_textbox.insert("0.0", self.placeholder_text)
            # When restoring, set the text color back to the placeholder color (gray)
            self.text_input_textbox.configure(text_color="gray")


# Example usage (for testing independently):
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("200x100")
#     root.title("Main App")
#
#     def open_mood():
#         mood_window = MoodInputWindow(master=root)
#         root.wait_window(mood_window)
#
#         if hasattr(mood_window, 'selected_color') and mood_window.selected_color is not None:
#              print(f"Main app received color: {mood_window.selected_color}")
#              print(f"Main app received emotion: {mood_window.selected_emotion}")
#              print(f"Main app received text: '{mood_window.optional_text}'")
#         else:
#              print("Mood window closed or no color selected.")
#
#     button = ctk.CTkButton(master=root, text="Open Mood Input", command=open_mood)
#     button.pack(pady=20)
#
#     root.mainloop()
