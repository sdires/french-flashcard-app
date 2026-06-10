# ==============================================================================
# MULTILINGUAL FLASH CARD APP WITH AUDIO PIPELINE
# ==============================================================================

from data_manager import DataManager
from audio_engine import AudioEngine
from flashcard_ui import FlashcardUI


def main():
    # 1. Spin up the background engines
    data_engine = DataManager()
    audio_engine = AudioEngine()

    # 2. Inject both engines straight into the UI frame
    # The UI takes the steering wheel from here!
    FlashcardUI(data_manager=data_engine, audio_engine=audio_engine)


if __name__ == "__main__":
    main()
