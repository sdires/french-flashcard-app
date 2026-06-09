# Multilingual French Flash Card App (v1.0)

A dynamic, desktop-based flashcard application built in Python using **Tkinter** and **Pandas**. The application features an integrated, asynchronous audio pipeline powered by **Google Text-to-Speech (gTTS)** and **Pygame** to provide native French and English pronunciations on the fly.

---

## 🚀 Key Features

* **Progress Persistence:** Automatically filters out vocabulary you already know and tracks your active study state dynamically by writing to a local user save file (`words_to_learn.csv`).
* **Dual-Language Native Audio Engine:** Connects to the Google TTS cloud API to generate high-quality, authentic pronunciations for both the French target word and its English translation.
* **Automated Deck Carousel:** Implements a background timer thread that automatically handles card-flipping intervals (4 seconds) to encourage hands-free rapid immersion.
* **Defensive Error Guardrails:** Engineered with layered try-except blocks to gracefully manage missing asset dependencies or sudden environment shifts without freezing or crashing the graphical interface.

---

## ⚠️ Technical Limitations & Boundaries

While the application is fully functional and optimized for self-paced study, users and developers should note the following architectural boundaries in this initial release:

### 1. Network Constraints & Audio Disruption
* **Cloud API Dependency:** The pronunciation engine relies strictly on the Google Text-to-Speech API. It requires an active internet connection to download voice assets on the fly.
* **Disruption Lockout:** If network connectivity drops mid-session, the application is engineered defensively to switch permanently to a "silent mode" to prevent the user interface from throwing endless warning popups or locking up your screen. Audio capabilities will not dynamically reconnect during that specific session; they require a stable internet connection and an application restart to re-initialize.

### 2. Audio File IO Overwrite System
* **Single-File Buffer:** Every time a flashcard displays a word, the audio data overwrites a single local file named `pronunciation.mp3`. 
* **Input Latency:** Clicking through cards exceptionally fast (faster than disk write speeds) can occasionally cause minimal file-access latency on standard mechanical storage drives, though it remains seamlessly fast for standard human study cadences.

### 3. File System Guarding & Paths
* **Relative Path Vulnerability:** The application searches for user interfaces and database sheets using local relative paths (`data/` and `images/`). 
* **Launch Directory Strictness:** The script must be executed directly from its root project directory. If run from a separate terminal working directory, Python will fail to locate asset mappings, resulting in a startup crash.
* **CSV Structural Integrity:** The state-saver engine expects that `data/words_to_learn.csv` maintains its exact tabular header structure (`French,English`). Modifying or deleting these columns manually outside the software environment will break the internal Pandas serialization loops.

### 4. Stateful Scalability
* **In-Memory Volatility:** The runtime deck logic pulls cards dynamically from a volatile in-memory dictionary array. While your overall progress saves to a CSV file when you hit the checkmark box, any words updated during a sudden power loss or ungraceful terminal termination won't register to disk until the data-saving thread block finishes executing.

---

## 🛠️ Project File Architecture

The application relies on a clean, professional directory structure. Datasets, visual assets, and system scripts are strictly grouped to maintain environment isolation:

```text
├── main.py                     # Primary execution script and application controller
├── pronunciation.mp3           # Dynamic cache file used for real-time audio playback
└── data/                       # Core Data Store Folder
    ├── french_words.csv        # Immutable master database containing 1,000+ vocabulary pairs
    └── words_to_learn.csv      # Stateful user progress database (generated automatically at runtime)
└── images/                     # Graphical Assets Folder
    ├── card_front.png          # Visual styling texture for the active target language side
    ├── card_back.png           # Visual styling texture for the active translation side
    ├── right.png               # Graphic asset for the 'Known Word' (Checkmark) button
    └── wrong.png               # Graphic asset for the 'Unknown Word' (Cross) button