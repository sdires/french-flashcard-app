# =======================================================================================================
# DEPENDENCIES & CORE SYSTEM ENGINES
# =======================================================================================================
import os                       # Crucial for dynamic, cross-platform absolute path calculations
import sys                      # Used to shut down the app cleanly if critical data assets are missing
from tkinter import messagebox  # Explicitly import the sub-module for UI pop-up dialogs
import pandas                   # Used for robust CSV data loading and processing
from random import choice       # Used to pull a single random item from the word list

# Note on messagebox: In Tkinter, sub-modules like messagebox must be explicitly
# imported by name; they do not automatically load when doing a standard 'import tkinter'.
# =======================================================================================================


class DataManager:
    def __init__(self):
        """Initializes the data tracking matrices, establishes local system paths, and loads the active deck."""
        self.words_to_learn_dict = []
        self.current_card = {}

        # ------------------- 🌍 Dynamic Absolute Path Calculation ------------------- #
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.words_to_learn_path = os.path.join(self.base_dir, 'data', 'words_to_learn.csv')
        self.master_words_path = os.path.join(self.base_dir, 'data', 'french_words.csv')

        # 2. Call the setup loader to ingest user state from local storage files
        self._load_initial_dataset()

    # ======================================================================================
    # 🧱 INTERNAL STORAGE INGESTION HELPERS
    # ======================================================================================

    def _load_initial_dataset(self):
        """INTERNAL: Attempts to read the persistent progress deck, falling back to the master list if missing."""
        try:
            # Try to read the user's saved progress file from historical runs
            self.words_to_learn_df = pandas.read_csv(self.words_to_learn_path)
            self.words_to_learn_dict = self.words_to_learn_df.to_dict('records')
        except (FileNotFoundError, pandas.errors.EmptyDataError):
            # 🔄 If progress file is missing OR completely blank, fall back to master list
            self._reset_to_master_deck()

    def _reset_to_master_deck(self):
        """INTERNAL: Cleans out runtime memory structures and reloads the full vocabulary pool from scratch."""
        try:
            self.words_to_learn_df = pandas.read_csv(self.master_words_path)
            self.words_to_learn_dict = self.words_to_learn_df.to_dict('records')
        except FileNotFoundError:
            # Ultimate safety check: if the engine can't even find the master asset, stop execution
            messagebox.showerror(
                title="Data Missing",
                message="Critical Error: Could not locate master vocabulary assets."
            )
            sys.exit()

    # ======================================================================================
    # PUBLIC DATA MUTATION LAYER (SRP INTERFACE)
    # ======================================================================================

    def get_random_card(self):
        """PUBLIC: Selects a random word token. Resets the collection automatically if fully cleared."""
        if not self.words_to_learn_dict:
            messagebox.showinfo(
                title="Congratulations!",
                message="You have learned every single word in this deck! 🎉\n\n"
                        "The flashcard deck will now reset to the master list so you can review again."
            )
            # 🔄 Reinitialize data frames mid-game using internal mechanics
            self._reset_to_master_deck()

        self.current_card = choice(self.words_to_learn_dict)
        return self.current_card

    def remove_current_card(self, card_to_remove):
        """PUBLIC: Drops a validated card out of the runtime list and updates state tracking files."""
        try:
            # Drop it from our live list sitting in volatile memory (RAM)
            self.words_to_learn_dict.remove(card_to_remove)
            updated_df = pandas.DataFrame(self.words_to_learn_dict)

            # Overwrite the tracking file with remaining words
            updated_df.to_csv(self.words_to_learn_path, index=False)
        except ValueError:
            # Safeguard case if the card structural footprint isn't located inside the array matrix
            pass

    # ======================================================================================
    # 🚨 EMERGENCY STATE SYNCHRONIZATION (RAM TO DISK)
    # ======================================================================================

    def force_save_current_state(self):
        """PUBLIC: Forces an immediate, synchronous dump of the active in-memory dataset to the disk.

        Acts as a safety net during sudden application shutdowns to prevent user progress loss.
        """
        # 1. Convert the active live dictionary/list state back into a structural pandas DataFrame
        updated_dataframe = pandas.DataFrame(self.words_to_learn_dict)

        # 2. Hard-write the matrix straight to your absolute CSV data pathing location
        updated_dataframe.to_csv(self.words_to_learn_path, index=False)

        print("💾 Emergency Backup Engine: RAM data safely synchronized to permanent disk storage.")