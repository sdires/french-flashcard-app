# ==============================================================================
# CAPSTONE PROJECT: MULTILINGUAL FLASH CARD APP WITH AUDIO PIPELINE
# ==============================================================================

# ---------------------------- Core UI & Data Frameworks ----------------------- #
from tkinter import *
from tkinter import messagebox  # Explicitly import the sub-module for UI pop-up dialogs
from random import choice       # Used to pull a single random item from the word list
import pandas                   # Used for robust CSV data loading and processing

# ---------------------------- Audio Engine Stack ------------------------------ #
# gTTS serves as the 'Brain' (generates native speech audio over API)
# Pygame serves as the 'Throat' (manages the background hardware audio playback stream)
from gtts import gTTS
import pygame                    # pip install pygame-ce

# ---------------------------- System Utilities -------------------------------- #
import sys  # Used to shut down the app cleanly if critical data assets are missing

# --- Initialize Audio Mixer ---
# Initialize the pygame mixer right at launch so it's ready to play clips instantly
pygame.mixer.init()

# ---------------------------- Configuration Constants ------------------------- #
BACKGROUND_COLOR = "#B1DDC6"  # Soft pastel green background hex code
FONT_NAME = "Ariel"           # Uniform font style used across canvas labels

# ---------------------------- Global State Registry -------------------------- #
french_word = "Word"     # Tracks the active target language string
english_word = None      # Tracks the active translation language string
timer = None             # Stores the current window.after() ID to cleanly manage background threads
chosen_dic = {}          # Tracks the active dictionary pair globally (e.g., {'French': 'Oui', 'English': 'Yes'})
audio_enabled = True     # Tracks if the audio engine is healthy and connected (Version 1 Toggle)


# ---------------------------- Word Dictionary Setup -------------------------- #

try:
    # 1. First choice: Load progress from previous study sessions
    french_word_df = pandas.read_csv('data/words_to_learn.csv')
except FileNotFoundError:
    try:
        # 2. Second choice: Fallback to the master list if no save file exists
        french_word_df = pandas.read_csv('data/french_words.csv')
    except FileNotFoundError:
        # 3. Ultimate Safety: If BOTH files are missing, show an error and close gracefully
        messagebox.showerror(
            title="Data Missing",
            message="Critical Error: Could not find any source vocabulary CSV files in the 'data/' directory."
        )
        sys.exit() # Cleanly shuts down the script instead of letting it crash further down

# 4. Safe Conversion: This line is only reached if french_word_df was successfully created above
# Convert the pandas DataFrame into a list of dictionaries: [{'French': '...', 'English': '...'}, ...]

french_word_dict = french_word_df.to_dict('records')

# ---------------------------- State manager  ------------------------------- #

# if ❌ pressed display English word and then show the next French word
# if ✅ show the translated English word, but remove the known French word from the dict

def state_manager(event):
    """
    Acts as the controller for manual user inputs (button clicks).
    Cancels existing background loops, triggers visual card flipping,
    updates database lists, and schedules the next card progression.
    """
    global timer

    # 1. Intercept and clear the active 3-second automatic flipping timer immediately
    window.after_cancel(timer)

    # 2. Visually flip to the English translation to give the user immediate feedback
    reveal_english_static()

    # 3. Inspect the event object to see exactly which button triggered the click
    button_object = event.widget

    # 4 Only run this block if the user clicks the checkmark button
    if button_object == known_button:
        # If the user knew the word, remove it from the runtime list rotation
        if chosen_dic in french_word_dict:
            french_word_dict.remove(chosen_dic)

            # Reconstruct the DataFrame without the learned word and save to CSV
            word_to_learn_df = pandas.DataFrame(french_word_dict)
            word_to_learn_df.to_csv('data/words_to_learn.csv', index=False)


    # 5. Schedule a controlled 2-second delay on the English answer before moving to the next card
    timer = window.after(2000, display_next_word)


# _______________________ Display Logic and Timing Chains ____________________#


# --- 🔊 Pronunciation Engine ---

def pronounce_word(word, language):
    """Generates and plays native audio. If it fails once, disables future audio spam."""
    global audio_enabled

    # If audio was previously flagged as broken/offline, silently skip it
    if not audio_enabled:
        return

    try:
        # 1. Stop any audio clip currently playing so sounds don't overlap
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        # 2. Convert the text to French audio ('fr') via Google TTS
        tts = gTTS(text=word, lang=language)
        tts.save("pronunciation.mp3")

        # 3. Load the audio file and play it out loud
        pygame.mixer.music.load("pronunciation.mp3")
        pygame.mixer.music.play()
    except Exception as e:
        # Fallback safeguard: If internet disconnects, print the error to console but don't crash the UI
        print(f"Audio Error: {e}")

        # Turn off the audio flag so this block skips on subsequent cards
        audio_enabled = False

        # This will pop up a gentle warning box over your Tkinter app exactly once
        messagebox.showwarning(
            title="Audio Offline",
            message="Could not load pronunciation. Please check your internet connection to use audio features."
        )

def display_french_word():
    """
    Selects a random word dictionary item from the active pool and renders
    it onto the front styling elements of the canvas card layout.
    """
    global french_word, english_word, chosen_dic

    # End game check: Trigger a victory banner if the dictionary list drops down to zero
    if len(french_word_dict) == 0:
        messagebox.showinfo(title="Victory!", message="You've mastered all the cards!")
        return

    # Randomly extract a dictionary item from our array
    chosen_dic = choice(french_word_dict)
    french_word = chosen_dic['French']
    english_word = chosen_dic['English']

    # Update Canvas UI properties to match the front (French) configuration
    my_canvas.itemconfig(card_background, image = card_front_img)
    my_canvas.itemconfig(card_title, fill = "black",text = "French")
    my_canvas.itemconfig(card_word, fill = "black", text = french_word)

    pronounce_word(french_word, "fr")



def display_next_word():
    """
    A unified wrapper function used to cycle standard card changes.
    Renders the layout text and simultaneously sets the automatic 3-second flip clock.
    """
    display_french_word()
    start_flip_timer()

def reveal_english_static():
    """
    Modifies canvas card assets to show the back (English translation).
    This function performs no timer setups, making it safe for button clicks.
    """
    my_canvas.itemconfig(card_background, image=card_back_img)
    my_canvas.itemconfig(card_title, fill="white", text="English")
    my_canvas.itemconfig(card_word, fill="white", text=english_word)

    pronounce_word(english_word, "en")

def display_english_word():
    """
    Triggered when an automatic idle cycle finishes. Shows the translation
    and schedules a 4-second idle delay before automatically requesting another card.
    """
    global timer
    # Visually show the word
    reveal_english_static()

    # Re-arm the automatic loop pendulum to pull a new card if no button is pushed
    # If the user doesn't press anything, wait another 3 seconds
    # on the English card, then automatically fetch the next French word!
    timer = window.after(4000, display_next_word)

def start_flip_timer():
    """
    Initializes a 4-second background wait loop before turning over the active card to English.
    """
    global timer
    timer = window.after(4000, display_english_word)



# ---------------------------- UI SETUP ------------------------------- #

# ___ Root Window Configuration ___

window = Tk()
window.title('FRENCH FLASH CARD')
window.config(bg = BACKGROUND_COLOR, padx = 50, pady = 50)

# ___ Canvas and Image Element Handling ___

my_canvas = Canvas(window, width = 800, height = 526, bg = BACKGROUND_COLOR, highlightthickness = 0)
card_front_img = PhotoImage(file = "images/card_front.png")
card_back_img = PhotoImage(file = "images/card_back.png")
card_background = my_canvas.create_image(400, 263, image = card_front_img)

# Layer texts on top of coordinates within the active canvas bounding box
card_title = my_canvas.create_text(400, 150, text = 'Title',  font = (FONT_NAME, 40, "italic"))
card_word = my_canvas.create_text(400, 263, text = 'Word', font = (FONT_NAME, 60, "bold"))

my_canvas.grid(row = 0, column = 0, columnspan = 2)

# ___ Widget Declarations ___

# ✅ (Known Word Button)
check_button_image = PhotoImage(file = "images/right.png")
known_button = Button(image = check_button_image, highlightthickness = 0)
known_button.grid(row = 1, column = 1)

# ❌ (Unknown Word Button)
x_button_image = PhotoImage(file = "images/wrong.png")
unknown_button = Button(image = x_button_image, highlightthickness = 0)
unknown_button.grid(row = 1, column = 0)

# --- Dynamic Input Binding Operations ---
# We bind the left mouse click ('<Button-1>') to pass tracking events directly
# to our custom state_manager instead of utilizing standard command functions.
unknown_button.bind('<Button-1>', state_manager)
known_button.bind('<Button-1>', state_manager)

# Kick off the very first card when the application window initializes
display_next_word()


window.mainloop()