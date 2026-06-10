# Multilingual French Flash Card App (v2.0)

A dynamic, highly resilient desktop-based flashcard application built in Python using **Tkinter** and **Pandas**. The application features an elegant **Single Responsibility Principle (SRP)** architecture with a decoupled, self-healing audio pipeline powered by **Google Text-to-Speech (gTTS)** and **Pygame** to provide native French and English pronunciations dynamically.

---

## 🚀 Key Features

* **Single Responsibility Architecture (SRP):** Completely decouples data management, graphical user interface rendering, and hardware audio streams into isolated, modular classes for maximum maintainability.
* **Progress Persistence:** Automatically filters out vocabulary you already know and tracks your active study state dynamically by updating your local user save file (`words_to_learn.csv`).
* **Dual-Language Native Audio Engine:** Connects to the Google TTS cloud API to generate high-quality, authentic pronunciations for both the French target word and its English translation.
* **Intelligent Polling & Self-Healing Audio:** Features a resilient retry mechanism that smoothly steps back during network drops to keep the UI snappy, alerts the user exactly *once* via an OS-native dialog box, and automatically attempts to reconnect every 5 displays.
* **Cross-Platform Absolute Pathing:** Built with dynamic runtime path calculations, making the application completely immune to execution directory constraints or operating system file-slash variance.
* **Defensive Error Guardrails:** Engineered with layered, nested try-except blocks, emergency script ejection routines (`sys.exit()`), and an OS window-intercept protocol to guarantee runtime progress is flushed to disk before shutdown.

---

## 🛠️ Architectural Safeguards & Features

This release introduces an enterprise-grade refactor addressing runtime stability, file lifecycle management, and network fluctuation:

### 1. Self-Healing Network & Audio Polling
* **Immediate Fail-Safe Cooldown:** The audio engine monitors connection attempts. If a connection drops, the engine immediately enters a non-blocking cooldown state to preserve lightning-fast UI card transitions.
* **Single-Alert Lockout:** Instead of flooding the interface with relentless error popups, the user is alerted exactly *once* per network drop event. 
* **Automatic Reconnection:** Every 5 cards displayed during a muted phase, the engine automatically runs a background probe to see if the internet connection has recovered. If successful, it unmutes audio and resets the warning gates seamlessly.

### 2. Audio File IO Lock Management
* **Active Memory Unloading:** To avoid standard OS file-lock crashes (`PermissionError`), the playback pipeline explicitly calls `pygame.mixer.music.stop()` and `pygame.mixer.music.unload()` before overwriting the single local cache asset (`pronunciation.mp3`).
* **Input Latency Mitigation:** Sound asset streaming is entirely abstracted from the core GUI thread layout, allowing robust user card-flipping interactions without micro-stutters.

### 3. Bulletproof File System Paths
* **Dynamic Location Calculation:** Rather than relying on fragile local relative paths, the code leverages Python's built-in `os` library to calculate absolute paths relative to where the execution script physically sits. 
* **Launch Directory Freedom:** The application can be safely run from any terminal working directory, shortcuts, or external scripts without triggering database mapping lookup failures.
* **Ejection Seat Error Handling:** If critical underlying CSV assets are physically missing entirely from the disk, the data manager captures the `FileNotFoundError`, warns the user cleanly via a Tkinter `messagebox`, and fires `sys.exit()` to terminate execution safely.

### 4. Direct-Write & Shutdown Data Synchronization
* **Zero In-Memory Volatility:** To combat progress loss during unexpected system power cuts or aggressive window terminations, the application implements two layers of data-flushing.
* **Immediate Progress Savings:** The moment a card is marked as known, the application strips it from runtime memory and immediately burns the remaining deck update directly to the hard drive via `.to_csv()`.
* **Graceful OS Close Interception:** The UI registers a window protocol hook (`WM_DELETE_WINDOW`) that intercepts native operating system "X" button clicks. This freezes the shutdown sequence, forces the data manager to synchronously dump all volatile RAM states safely onto the hard disk, and then cleanly terminates background process loops.

---

## 📂 Project File Architecture

The application relies on a clean, professional directory structure. Datasets, visual assets, and system scripts are strictly grouped to maintain modular environment isolation:

```text
├── audio_engine.py             # Self-healing audio pipeline and gTTS manager
├── data_manager.py             # Data I/O layer, absolute path calculator, and progress saver
├── flashcard_ui.py             # Core Tkinter layout, timer control layer, and user interface engine
├── main.py                     # Primary execution controller and script entry-point
├── pronunciation.mp3           # Dynamic cache file used for real-time audio playback
└── data/                       # Core Data Store Folder
    ├── french_words.csv        # Immutable master database containing 1,000+ vocabulary pairs
    └── words_to_learn.csv      # Stateful user progress database (generated automatically at runtime)
└── images/                     # Graphical Assets Folder
    ├── card_front.png          # Visual styling texture for the active target language side
    ├── card_back.png           # Visual styling texture for the active translation side
    ├── right.png               # Graphic asset for the 'Known Word' (Checkmark) button
    └── wrong.png               # Graphic asset for the 'Unknown Word' (Cross) button