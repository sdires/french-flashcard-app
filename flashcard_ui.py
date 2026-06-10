# ======================================================================================
# DEPENDENCIES & CORE SYSTEM ENGINES
# ======================================================================================
import os  # Crucial for dynamic, cross-platform absolute path calculations
from tkinter import *  # Standard GUI toolkit for layout, widgets, and windows

# ======================================================================================

# ---------------------------- Configuration Constants ------------------------- #
BACKGROUND_COLOR = "#B1DDC6"  # Soft pastel green background hex code
FONT_NAME = "Arial"  # Uniform font style used across canvas labels


class FlashcardUI:
    def __init__(self, data_manager, audio_engine):
        """Initializes the graphical workspace, links backing engines, and fires the launch sequence."""
        self.audio_engine = audio_engine
        self.data_manager = data_manager
        self.current_card = {}
        self.timer = None
        self.is_flipped = False  # Track state: False = French Front, True = English Back

        # 1. Initialize the main root window framework
        self.window = Tk()
        self.window.title("FLASH CARD")
        self.window.config(bg=BACKGROUND_COLOR, padx=50, pady=50)

        # 🚨 LIFE CYCLE INTERCEPTOR: Bind OS Close ("X") button to safe saving sequence
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 🌍 Calculate the absolute directory path to locate system textures safely from anywhere
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. Call the internal setup worker to construct canvas matrices and buttons
        self._create_widgets()

        # 3. Kick off the continuous loop sequence with the first card immediately
        self._get_next_card()

        # 4. Hand execution control over to the application graphical loop
        self.window.mainloop()

    # ======================================================================================
    # 🧱 INTERNAL UI CONSTRUCTION HELPERS
    # ======================================================================================

    def _create_widgets(self):
        """INTERNAL: Dedicated strictly to drawing the canvas texture maps and structural button widgets."""
        self.canvas = Canvas(self.window, width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)

        # Pull asset paths using structural absolute formatting for execution stability
        self.card_front_img = PhotoImage(file=os.path.join(self.base_dir, "images", "card_front.png"))
        self.card_back_img = PhotoImage(file=os.path.join(self.base_dir, "images", "card_back.png"))

        self.card_background = self.canvas.create_image(400, 263, image=self.card_front_img)

        # Layer textual configurations cleanly over canvas coordinates
        self.card_title = self.canvas.create_text(400, 150, font=(FONT_NAME, 40, "italic"))
        self.card_word = self.canvas.create_text(400, 263, font=(FONT_NAME, 60, "bold"))
        self.canvas.grid(row=0, column=0, columnspan=2)

        # ___ Smart Button Mapping & Asset Binding ___

        # ✅ (Known / Right Button) -> Linked to custom state handler
        self.check_button_image = PhotoImage(file=os.path.join(self.base_dir, "images", "right.png"))
        self.known_button = Button(image=self.check_button_image, highlightthickness=0,
                                   command=self.handle_right_button)
        self.known_button.grid(row=1, column=1)

        # ❌ (Unknown / Wrong Button) -> Linked to custom state handler
        self.x_button_image = PhotoImage(file=os.path.join(self.base_dir, "images", "wrong.png"))
        self.unknown_button = Button(image=self.x_button_image, highlightthickness=0,
                                     command=self.handle_wrong_button)
        self.unknown_button.grid(row=1, column=0)

    def _update_display(self, title, word, color="black", is_front=True):
        """INTERNAL: Small, reusable presentation function handling texture swaps and label changes."""
        self.canvas.itemconfig(self.card_title, fill=color, text=title)
        self.canvas.itemconfig(self.card_word, fill=color, text=word)
        if is_front:
            self.canvas.itemconfig(self.card_background, image=self.card_front_img)
        else:
            self.canvas.itemconfig(self.card_background, image=self.card_back_img)

    # ======================================================================================
    # 🧠 INTERNAL DATA & UI RENDERING LAYER (SRP ISOLATION)
    # ======================================================================================

    def _get_next_card(self):
        """INTERNAL: Mutate Data State Only."""
        self.current_card = self.data_manager.get_random_card()
        self._show_front_card()

    def _show_front_card(self):
        """INTERNAL: Render Front UI Components Only."""
        self.is_flipped = False
        self._update_display("French", self.current_card["French"], color="black", is_front=True)
        self.audio_engine.pronounce_word(self.current_card["French"], language="fr")

        # Hand tracking off to the control loop
        self._schedule_flip_timer()

    def _flip_card(self):
        """INTERNAL: Render Back UI Components Only."""
        self._cancel_active_timer()
        self.is_flipped = True
        self._update_display("English", self.current_card["English"], color="white", is_front=False)
        self.audio_engine.pronounce_word(self.current_card["English"], language="en")
        # ⏱️ HANDS-FREE LOOP PART B: Tell the control layer to pull a new card after 2 seconds!
        self._schedule_advance_timer(delay=2000)

    # ======================================================================================
    # PUBLIC STATE-AWARE MASTER BUTTON ROUTERS
    # ======================================================================================

    def handle_right_button(self):
        """PUBLIC: Input Handler. Processes a correct card based cleanly on viewport state."""
        self._cancel_active_timer()  # Top-line anti-spam protection
        self.data_manager.remove_current_card(self.current_card)

        if not self.is_flipped:
            # If on French front: Flip to show them the answer, then queue a brief reading pause
            self._flip_card()
            self._schedule_advance_timer(delay=1500)
        else:
            # If already on English back: Cycle to a completely fresh card instantly
            self._get_next_card()

    def handle_wrong_button(self):
        """PUBLIC: Input Handler. Processes a skipped/failed card based cleanly on viewport state."""
        self._cancel_active_timer()  # Top-line anti-spam protection

        if not self.is_flipped:
            # If on French front: Flip to reveal what they missed, then queue a reading pause
            self._flip_card()
            self._schedule_advance_timer(delay=2000)
        else:
            # If already on English back: Cycle forward immediately
            self._get_next_card()

    # ======================================================================================
    # ⏳ INTERNAL CONTROL LAYER (TIMER MICRO-MANAGEMENT)
    # ======================================================================================

    def _schedule_flip_timer(self):
        """INTERNAL: Automatic flip countdown orchestration."""
        self._cancel_active_timer()
        self.timer = self.window.after(3000, self._flip_card)

    def _schedule_advance_timer(self, delay):
        """INTERNAL: Post-interaction reading pause countdown orchestration."""
        self._cancel_active_timer()
        self.timer = self.window.after(delay, self._get_next_card)

    def _cancel_active_timer(self):
        """INTERNAL: Thread Cleanup Only."""
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None

    # ======================================================================================
    # 🚨 INTERNAL GRACEFUL EMERGENCY SHUTDOWN ROUTINE
    # ======================================================================================

    def _on_closing(self):
        """INTERNAL: Intercepts OS window kill signal to safely back up RAM state to disk."""
        print("🚨 Close signal received! Executing emergency dataset disk sync...")
        try:
            self.data_manager.force_save_current_state()
            print("💾 Cloud/Local state backup sequence completed successfully.")
        except Exception as e:
            print(f"❌ Critical Error: Failed to flush runtime state to disk during crash sequence: {e}")

        self.window.destroy()