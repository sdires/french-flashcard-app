# =======================================================================================================
# DEPENDENCIES & CORE SYSTEM ENGINES
# =======================================================================================================
import os                          # Crucial for dynamic, cross-platform absolute path calculations
from gtts import gTTS              # Google Text-to-Speech: Converts string text to native audio mp3s
import pygame                      # Handles multi-media operations (pip install pygame-ce)
from tkinter import messagebox     # Explicitly imported sub-module for OS-native alert dialog windows

# Note on messagebox: In Tkinter, sub-modules like messagebox must be explicitly
# imported by name; they do not automatically load when doing a standard 'import tkinter'.
# gTTS serves as the 'Brain' (generates native speech audio over API)
# Pygame serves as the 'Throat' (manages the background hardware audio playback stream)
# =======================================================================================================


class AudioEngine:
    def __init__(self):
        """Initializes core audio system frameworks, dynamic path nodes, and self-healing trackers."""
        # --- Initialize Audio Stream Pipelines ---
        pygame.init()                   # Initializes the core engine wrapper
        pygame.mixer.init()             # Initializes the sound hardware mixer

        # ---------------------------- Configuration Constants ------------------------- #
        self._COOLDOWN_LIMIT = 5        # Number of displays to skip before server reconnection test

        # ------------------------ Advanced Self-Healing State Trackers ---------------- #
        self._audio_enabled = True      # Internal master control flag for active playback
        self._failed_attempts = 0       # Sequential breakdown counter
        self._has_warned_user = False   # Gateway latch to prevent alert window spamming
        self._cooldown_counter = 0      # Iteration tracking index during quiet execution phases

        # 🌍 Calculate the absolute path for the mp3 file ONCE at launch
        self._base_dir = os.path.dirname(os.path.abspath(__file__))
        self._mp3_path = os.path.join(self._base_dir, "pronunciation.mp3")

    # ======================================================================================
    # 🧱 INTERNAL SERVER HEALTH & COOLDOWN ORCHESTRATION
    # ======================================================================================

    def _process_cooldown_lifecycle(self):
        """INTERNAL: Monitors and increments the card skipping indexes while audio servers are isolated."""
        self._cooldown_counter += 1

        # Check if the mandatory structural skip barrier has been surpassed
        if self._cooldown_counter >= self._COOLDOWN_LIMIT:
            print("🔄 5 displays passed. Attempting to reconnect to audio server...")
            self._audio_enabled = True
            self._cooldown_counter = 0  # Reset matrix tracking pointer

    def _handle_system_fault(self, exception_log):
        """INTERNAL: Enforces safety protocols, triggers non-blocking cooldown state, and warns once."""
        self._failed_attempts += 1
        print(f"Audio Failure ({self._failed_attempts} consecutive): {exception_log}")

        # Drop into isolated status immediately to protect the main graphical loop from thread lag
        self._audio_enabled = False
        self._cooldown_counter = 0

        # Launch individual warning notification alert window on the immediate initial failure sequence
        if not self._has_warned_user and self._failed_attempts >= 1:
            self._has_warned_user = True  # Latch the gate completely

            messagebox.showwarning(
                title="Audio Issues Detected",
                message="The app is having trouble reaching the audio servers.\n\n"
                        "We will temporarily mute audio to keep your session smooth, "
                        "but we will automatically retry connecting every 5 cards!"
            )

    # ======================================================================================
    # PUBLIC PRONUNCIATION INTERFACE (SRP DISPATCH ENGINE)
    # ======================================================================================

    def pronounce_word(self, word, language):
        """PUBLIC: Converts raw textual tokens into audio playback while managing state-aware connection faults."""
        # 1. Block operations if system is actively cooling down from a connectivity block
        if not self._audio_enabled:
            self._process_cooldown_lifecycle()
            return

        try:
            # 2. Release hardware resource locks on files residing inside persistent storage disks
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            # 3. Stream payloads from remote cloud endpoints and map blocks locally
            tts = gTTS(text=word, lang=language)
            tts.save(self._mp3_path)

            # 4. Ingest absolute storage paths and fire background hardware playback threads
            pygame.mixer.music.load(self._mp3_path)
            pygame.mixer.music.play()

            # 🎉 SUCCESS CONTEXT: Flush operational failure flags back to baseline positions
            self._failed_attempts = 0
            self._has_warned_user = False

        except Exception as e:
            # ❌ FAILURE CONTEXT: Route control variables safely into the fault management engine
            self._handle_system_fault(exception_log=e)