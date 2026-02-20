"""
Voice Assistant v4 — BMO GUI  (src/ui/app.py)

BMO-themed UI — the window is styled like the physical BMO device:

  ┌──────────────────────────────────────────────────────┐  ← CASE_TEAL shell
  │  ⬡ BMO · Voice Assistant v4          [⚙ Settings]  │
  │ ┌────────────────────────────────────────────────┐   │
  │ │              (phosphor-green SCREEN)            │   │  ← SCREEN_BG bezel
  │ │   [ORB]   STATE LABEL                   LEGEND │   │
  │ │  ─────────────────────────────────────────────  │   │
  │ │  CONVERSATION LOG                              │   │
  │ │   …chat bubbles…                               │   │
  │ │  [___  type a message  ___________________]    │   │
  │ └────────────────────────────────────────────────┘   │
  │   [● STOP]  [▶ LISTEN]  [✔ SEND]  [☰ MENU]          │  ← hardware btns
  └──────────────────────────────────────────────────────┘

Colour reference — BMO_Body (src/utils/config.py):
  CASE_TEAL   #5F9EA0   plastic shell
  SCREEN_BG   #D4EAC8   CRT screen
  BTN_RED     #FF6B6B   Stop / Cancel
  BTN_BLUE    #4ECDC4   Listen / Confirm
  BTN_GREEN   #2ECC71   Send / Execute
  BTN_DPAD    #F1C40F   Menu / Nav
  TEXT_DARK   #2C3E50   text on teal/green
  TEXT_LIGHT  #FFFFFF   text on buttons
"""
from __future__ import annotations

import threading
import time

from typing import Optional

import customtkinter as ctk

from src.utils.logger import get_logger
from src.utils.config import Config, BMO_Body as B
from src.utils.state_machine import StateMachine, AssistantState
from src.ui.face_widget import FaceWidget
from src.utils.conversation import ConversationManager
from src.core.wake import WakeWordDetector
from src.core.stt import STTEngine
from src.core.llm import LLMEngine, list_ollama_models
from src.core.tts import TTSEngine

log = get_logger("ui")

# ══════════════════════════════════════════════════════════════════════
# Palette — every colour reference uses BMO_Body constants (alias B)
# ══════════════════════════════════════════════════════════════════════
PALETTE = {
    # ── Shell (plastic case) ──────────────────────────────────────────
    "shell":        B.CASE_TEAL,          # outer window bg
    "shell_dark":   B.BEZEL,              # top/bottom bars, bezel frame
    # ── Screen ───────────────────────────────────────────────────────
    "screen":       B.SCREEN_BG,          # CRT phosphor-green face
    "screen_lt":    B.SURFACE_LT,         # lighter green for inputs
    # ── Overlays / drawers (deep navy) ───────────────────────────────
    "overlay":      B.SURFACE_DK,         # settings drawer bg
    "overlay_lt":   "#3d5166",            # lighter navy for hover/fields
    # ── Text ─────────────────────────────────────────────────────────
    "text_on_screen": B.TEXT_DARK,        # dark navy — readable on green
    "text_on_btn":  B.TEXT_LIGHT,         # white — readable on any button
    "text_dim":     "#4a6741",            # dimmed phosphor green
    # ── Chat bubbles (on the screen) ─────────────────────────────────
    "user_bubble":  "#c0dfb8",            # slightly deeper green tint
    "ai_bubble":    "#b8d4b0",            # even deeper — differentiate AI
    # ── Hardware button colours ───────────────────────────────────────
    "btn_stop":     B.BTN_RED,
    "btn_stop_h":   B.BTN_RED_H,
    "btn_listen":   B.BTN_BLUE,
    "btn_listen_h": B.BTN_BLUE_H,
    "btn_send":     B.BTN_GREEN,
    "btn_send_h":   B.BTN_GREEN_H,
    "btn_menu":     B.BTN_DPAD,
    "btn_menu_h":   B.BTN_DPAD_H,
    # ── State-indicator colours (used for orb + labels) ───────────────
    "idle":         B.BTN_BLUE,           # calm sky blue
    "listening":    B.BTN_RED,            # hot red
    "thinking":     B.BTN_DPAD,           # alert gold
    "speaking":     B.BTN_GREEN,          # active green
    "error":        B.BTN_RED,
    # ── Accent aliases (legacy / settings drawer) ─────────────────────
    "accent":       B.BTN_BLUE,
    "accent_h":     B.BTN_BLUE_H,
    "accent2":      B.CASE_TEAL,
    "border":       B.BEZEL,
    "border_dim":   "#3d6b6d",
    "bg":           B.SURFACE_DK,        # drawer background alias
    "surface":      "#243040",
    "surface2":     B.SURFACE_DK,
    "text":         B.TEXT_DARK,
    "thinking_lbl": B.BTN_DPAD,
}

STATE_COLORS = {
    AssistantState.IDLE:      PALETTE["idle"],
    AssistantState.LISTENING: PALETTE["listening"],
    AssistantState.THINKING:  PALETTE["thinking"],
    AssistantState.SPEAKING:  PALETTE["speaking"],
}

STATE_LABELS = {
    AssistantState.IDLE:      "IDLE  —  Waiting for wake word",
    AssistantState.LISTENING: "LISTENING  —  Recording…",
    AssistantState.THINKING:  "THINKING  —  Processing…",
    AssistantState.SPEAKING:  "SPEAKING  —  Playing response…",
}

ctk.set_appearance_mode("light")   # light mode so phosphor-green reads right
ctk.set_default_color_theme("blue")





# ══════════════════════════════════════════════════════════════════════
# ChatMessage — styled bubble that lives on the phosphor-green screen
# ══════════════════════════════════════════════════════════════════════
class ChatMessage(ctk.CTkFrame):

    def __init__(self, parent, role: str, text: str, timestamp: str, **kw):
        is_user = role == "user"
        border_col = B.BTN_BLUE if is_user else B.CASE_TEAL
        super().__init__(
            parent,
            fg_color=PALETTE["user_bubble"] if is_user else PALETTE["ai_bubble"],
            corner_radius=12,
            border_width=2,
            border_color=border_col,
            **kw,
        )
        badge_color = B.BTN_BLUE if is_user else B.CASE_TEAL
        ctk.CTkLabel(
            self,
            text=("  YOU  " if is_user else "  BMO  "),
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=B.TEXT_LIGHT,
            fg_color=badge_color,
            corner_radius=6,
        ).pack(anchor="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=B.TEXT_DARK,
            wraplength=440,
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(2, 4))

        ctk.CTkLabel(
            self,
            text=timestamp,
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=PALETTE["text_dim"],
        ).pack(anchor="e", padx=10, pady=(0, 6))


# ══════════════════════════════════════════════════════════════════════
# SettingsDrawer — slides in from the right, deep-navy overlay
# ══════════════════════════════════════════════════════════════════════
class SettingsDrawer(ctk.CTkFrame):

    def __init__(self, parent, app: "AssistantApp", **kw):
        super().__init__(
            parent,
            fg_color=PALETTE["overlay"],
            corner_radius=0,
            border_width=2,
            border_color=B.CASE_TEAL,
            **kw,
        )
        self.app = app
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        # Header
        ctk.CTkLabel(
            self,
            text="⚙  SETTINGS",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=B.BTN_DPAD,
        ).pack(pady=(20, 4), padx=20, anchor="w")

        ctk.CTkFrame(self, height=1, fg_color=B.CASE_TEAL).pack(
            fill="x", padx=16, pady=4)

        # ── Wake Word ─────────────────────────────────────────────────
        self._section("WAKE WORD")
        self.wake_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g. computer",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=PALETTE["overlay_lt"],
            border_color=B.CASE_TEAL,
            text_color=B.TEXT_LIGHT,
            height=36,
        )
        self.wake_entry.insert(0, self.app.config.wake_word)
        self.wake_entry.pack(fill="x", padx=16, pady=(4, 0))
        self._btn("Apply", B.BTN_DPAD, B.BTN_DPAD_H, self._apply_wake)

        # ── TTS Engine ────────────────────────────────────────────────
        self._section("TTS ENGINE")
        self.engine_var = ctk.StringVar(value=self.app.config.tts_engine)
        for label, val in [("pyttsx3 (Offline)", "pyttsx3"),
                           ("gTTS (Online)",     "gtts"),
                           ("Edge TTS (MS)",     "edge")]:
            ctk.CTkRadioButton(
                self, text=label, variable=self.engine_var, value=val,
                font=ctk.CTkFont(size=12), text_color=B.TEXT_LIGHT,
                fg_color=B.BTN_GREEN, hover_color=B.BTN_GREEN_H,
                command=self._apply_engine,
            ).pack(anchor="w", padx=20, pady=2)

        # ── TTS Speed ─────────────────────────────────────────────────
        self._section("TTS SPEED")
        self.speed_var = ctk.StringVar(value=self.app.config.tts_speed)
        for spd in ["slow", "normal", "fast"]:
            ctk.CTkRadioButton(
                self, text=spd.capitalize(), variable=self.speed_var,
                value=spd, font=ctk.CTkFont(size=12),
                text_color=B.TEXT_LIGHT,
                fg_color=B.BTN_BLUE, hover_color=B.BTN_BLUE_H,
                command=self._apply_speed,
            ).pack(anchor="w", padx=20, pady=2)

        # ── Ollama Model ──────────────────────────────────────────────
        self._section("OLLAMA MODEL")
        self._model_var = ctk.StringVar(value=self.app.llm.model)
        self.model_combo = ctk.CTkComboBox(
            self,
            variable=self._model_var,
            values=[self.app.llm.model],
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=PALETTE["overlay_lt"],
            border_color=B.CASE_TEAL,
            button_color=B.BTN_BLUE,
            button_hover_color=B.BTN_BLUE_H,
            text_color=B.TEXT_LIGHT,
            dropdown_fg_color=PALETTE["overlay"],
            dropdown_text_color=B.TEXT_LIGHT,
            dropdown_hover_color=PALETTE["overlay_lt"],
            height=36,
            state="readonly",
        )
        self.model_combo.pack(fill="x", padx=16, pady=(4, 0))

        btn_row = ctk.CTkFrame(self, fg_color=PALETTE["overlay"])
        btn_row.pack(fill="x", padx=16, pady=4)

        self._refresh_btn = ctk.CTkButton(
            btn_row, text="⟳ Refresh", height=30,
            font=ctk.CTkFont(size=11),
            fg_color=PALETTE["overlay_lt"],
            hover_color=PALETTE["shell_dark"],
            border_color=B.CASE_TEAL, border_width=1,
            text_color=B.CASE_TEAL,
            command=self._refresh_models,
        )
        self._refresh_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        ctk.CTkButton(
            btn_row, text="Apply", height=30,
            font=ctk.CTkFont(size=11),
            fg_color=B.BTN_GREEN, hover_color=B.BTN_GREEN_H,
            text_color=B.TEXT_LIGHT,
            command=self._apply_model,
        ).pack(side="right", expand=True, fill="x", padx=(4, 0))

        self._model_status = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=B.CASE_TEAL,
        )
        self._model_status.pack(anchor="w", padx=18, pady=(0, 4))

        # ── Clear History ─────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=B.CASE_TEAL).pack(
            fill="x", padx=16, pady=16)
        ctk.CTkButton(
            self, text="🗑  Clear History", height=36,
            font=ctk.CTkFont(size=12),
            fg_color=B.BTN_RED, hover_color=B.BTN_RED_H,
            text_color=B.TEXT_LIGHT,
            command=self.app.clear_history,
        ).pack(fill="x", padx=16, pady=4)

    # ------------------------------------------------------------------
    def _section(self, title: str):
        ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=B.CASE_TEAL,
        ).pack(anchor="w", padx=20, pady=(12, 2))

    def _btn(self, label, fg, hover, cmd):
        ctk.CTkButton(
            self, text=label, height=30,
            font=ctk.CTkFont(size=11),
            fg_color=fg, hover_color=hover,
            text_color=B.TEXT_DARK,
            command=cmd,
        ).pack(fill="x", padx=16, pady=(4, 0))

    # ------------------------------------------------------------------
    def _refresh_models(self):
        self._refresh_btn.configure(text="⟳ Loading…", state="disabled")
        self._model_status.configure(text="Querying Ollama…",
                                     text_color=B.CASE_TEAL)
        def fetch():
            models = list_ollama_models()
            self.after(0, self._populate_models, models)
        threading.Thread(target=fetch, daemon=True, name="ModelFetch").start()

    def _populate_models(self, models: list):
        self._refresh_btn.configure(text="⟳ Refresh", state="normal")
        if models:
            self.model_combo.configure(values=models)
            current = self._model_var.get()
            if current not in models:
                self._model_var.set(models[0])
                self.model_combo.set(models[0])
            self._model_status.configure(
                text=f"{len(models)} model(s) found.",
                text_color=B.BTN_GREEN)
        else:
            self._model_status.configure(
                text="No models — is Ollama running?",
                text_color=B.BTN_RED)

    def _apply_model(self):
        chosen = self._model_var.get().strip()
        if not chosen:
            return
        self.app.llm.set_model(chosen)
        self.app.after(0, self.app._model_lbl.configure,
                       {"text": f"LLM: {chosen}  |  STT: Groq Whisper"})
        self.app.add_system_message(f"Model switched → {chosen}")
        self._model_status.configure(text=f"Active: {chosen}",
                                     text_color=B.BTN_GREEN)

    def _apply_wake(self):
        word = self.wake_entry.get().strip().lower()
        if word:
            self.app.config.set("wake_word.word", word)
            self.app.add_system_message(f"Wake word → '{word}'")

    def _apply_engine(self):
        self.app.tts.set_engine(self.engine_var.get())
        self.app.add_system_message(f"TTS engine → {self.engine_var.get()}")

    def _apply_speed(self):
        self.app.tts.set_speed(self.speed_var.get())
        self.app.add_system_message(f"TTS speed → {self.speed_var.get()}")


# ══════════════════════════════════════════════════════════════════════
# AssistantApp — main window styled like the BMO device
# ══════════════════════════════════════════════════════════════════════
class AssistantApp(ctk.CTk):
    """Main application window."""

    DRAWER_WIDTH = 270

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

        # ── Backend ────────────────────────────────────────────────────
        self.state_machine = StateMachine()
        self.conversation  = ConversationManager(config)
        self.conversation.start_session()
        self.stt           = STTEngine(config)
        self.llm           = LLMEngine(config)
        self.tts           = TTSEngine(config)
        self.wake_detector: Optional[WakeWordDetector] = None

        # ── Window ─────────────────────────────────────────────────────
        self.title("BMO  —  Voice Assistant v4")
        w = config.get("ui.window_width", 1000)
        h = config.get("ui.window_height", 740)
        self.geometry(f"{w}x{h}")
        self.minsize(840, 620)
        self.configure(fg_color=B.CASE_TEAL)   # 🟦 BMO plastic shell

        self._drawer_open = False
        self._active_worker: Optional[threading.Thread] = None
        self._chat_row = 0

        self.state_machine.subscribe(self._on_state_change)
        self._build_layout()

        self.bind("<Control-l>",     lambda _: self._toggle_listening())
        self.bind("<Control-d>",     lambda _: self.clear_history())
        self.bind("<Control-comma>", lambda _: self._toggle_drawer())
        self.bind("<Escape>",        lambda _: self._stop_all())
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        log.info("AssistantApp ready.")

    # ══════════════════════════════════════════════════════════════════
    # Layout
    # ══════════════════════════════════════════════════════════════════

    def _build_layout(self):
        """
        Root:  [main_body | drawer]
        main_body:
            top_bar        ← CASE_TEAL strip
            bezel_frame    ← BEZEL frame containing the screen
              screen        ← SCREEN_BG phosphor-green panel
                visualizer  ← orb + state label
                chat_area   ← conversation log
                text_entry  ← inline text input
            hw_btn_bar     ← physical-style hardware buttons
        """
        self._root_frame = ctk.CTkFrame(self, fg_color=B.CASE_TEAL)
        self._root_frame.pack(fill="both", expand=True)

        # Main body (left) + drawer (right)
        self._main_body = ctk.CTkFrame(self._root_frame, fg_color=B.CASE_TEAL)
        self._main_body.pack(side="left", fill="both", expand=True)

        self._drawer = SettingsDrawer(self._root_frame, app=self)
        # Drawer hidden initially

        self._build_top_bar()
        self._build_screen()       # bezel + phosphor screen + contents
        self._build_hw_btn_bar()   # physical hardware buttons

    # ------------------------------------------------------------------
    def _build_top_bar(self):
        """BMO top strip — teal bar with title and tiny keyboard hints."""
        bar = ctk.CTkFrame(
            self._main_body,
            height=52,
            fg_color=B.BEZEL,
            corner_radius=0,
        )
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar, text="⬡  BMO",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=B.SCREEN_BG,
        ).pack(side="left", padx=18)

        ctk.CTkLabel(
            bar, text="Voice Assistant  v4",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=B.CASE_TEAL,
        ).pack(side="left")

        ctk.CTkLabel(
            bar, text="Ctrl+L · Ctrl+D · Esc",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=B.CASE_TEAL,
        ).pack(side="right", padx=12)

    # ------------------------------------------------------------------
    def _build_screen(self):
        """Bezel frame + phosphor-green CRT screen inside it."""
        # Bezel — slightly darker teal ring that frames the screen
        bezel = ctk.CTkFrame(
            self._main_body,
            fg_color=B.BEZEL,
            corner_radius=16,
            border_width=4,
            border_color=B.BEZEL,
        )
        bezel.pack(fill="both", expand=True, padx=14, pady=(8, 6))

        # Screen — the phosphor-green CRT face
        self._screen = ctk.CTkFrame(
            bezel,
            fg_color=B.SCREEN_BG,
            corner_radius=10,
        )
        self._screen.pack(fill="both", expand=True, padx=6, pady=6)

        self._build_visualizer()
        self._build_chat_area()
        self._build_text_entry()
        self._build_status_bar()

    # ------------------------------------------------------------------
    def _build_visualizer(self):
        """Top of screen: BMO face + state legend side-by-side."""
        panel = ctk.CTkFrame(self._screen, fg_color=B.SCREEN_BG, height=150)
        panel.pack(fill="x", padx=0, pady=0)
        panel.pack_propagate(False)

        # BMO Face (replaces the old Orb)
        self._face = FaceWidget(panel, fg_color=B.SCREEN_BG)
        self._face.pack(side="left", padx=(24, 8), pady=10)

        # State info
        info_col = ctk.CTkFrame(panel, fg_color=B.SCREEN_BG)
        info_col.pack(side="left", fill="y", pady=16)

        self._state_label = ctk.CTkLabel(
            info_col,
            text=STATE_LABELS[AssistantState.IDLE],
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=B.BTN_BLUE,
        )
        self._state_label.pack(anchor="w", pady=(20, 6))

        model_hint = ctk.CTkLabel(
            info_col,
            text=f"LLM: {self.llm.model}",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=PALETTE["text_dim"],
        )
        model_hint.pack(anchor="w")
        self._model_lbl = model_hint   # reused by drawer Apply

        # State legend (right side)
        legend = ctk.CTkFrame(panel, fg_color=B.SCREEN_BG)
        legend.pack(side="right", padx=20, pady=16, anchor="n")

        ctk.CTkLabel(
            legend, text="STATE",
            font=ctk.CTkFont(family="Consolas", size=8, weight="bold"),
            text_color=PALETTE["text_dim"],
        ).pack(anchor="w")

        for state, color in STATE_COLORS.items():
            row = ctk.CTkFrame(legend, fg_color=B.SCREEN_BG)
            row.pack(anchor="w", pady=1)
            ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=10),
                         text_color=color, width=18).pack(side="left")
            ctk.CTkLabel(row, text=state.name,
                         font=ctk.CTkFont(family="Consolas", size=9),
                         text_color=B.TEXT_DARK).pack(side="left", padx=2)

        # Thin separator line
        ctk.CTkFrame(self._screen, height=2,
                     fg_color=B.BEZEL).pack(fill="x", padx=10)

    # ------------------------------------------------------------------
    def _build_chat_area(self):
        """Scrollable conversation log — lives on the phosphor-green screen."""
        ctk.CTkLabel(
            self._screen, text="CONVERSATION LOG",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=PALETTE["text_dim"],
        ).pack(anchor="w", padx=16, pady=(6, 2))

        self._chat_scroll = ctk.CTkScrollableFrame(
            self._screen,
            fg_color=B.SCREEN_BG,
            scrollbar_button_color=B.BEZEL,
            scrollbar_button_hover_color=B.CASE_TEAL,
        )
        self._chat_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._chat_scroll.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def _build_text_entry(self):
        """Inline text entry bar at the bottom of the screen panel."""
        bar = ctk.CTkFrame(self._screen, fg_color=B.SCREEN_BG, height=52)
        bar.pack(fill="x", side="bottom", padx=10, pady=(2, 6))
        bar.pack_propagate(False)

        ctk.CTkFrame(self._screen, height=1,
                     fg_color=B.BEZEL).pack(fill="x", padx=10, side="bottom")

        self._text_entry = ctk.CTkEntry(
            bar,
            placeholder_text="Type a message and press Enter…",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=B.SURFACE_LT,
            border_color=B.BEZEL,
            text_color=B.TEXT_DARK,
            placeholder_text_color=PALETTE["text_dim"],
            height=36,
            corner_radius=18,
        )
        self._text_entry.pack(side="left", fill="x", expand=True,
                              padx=(0, 6), pady=8)
        self._text_entry.bind("<Return>", self._on_text_submit)

    # ------------------------------------------------------------------
    def _build_status_bar(self):
        """Tiny status strip at very bottom of the screen."""
        bar = ctk.CTkFrame(self._screen, height=20, fg_color=B.BEZEL,
                           corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            bar, text="Ready",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=B.SCREEN_BG, anchor="w",
        )
        self._status_lbl.pack(side="left", padx=10)

        ctk.CTkLabel(
            bar, text="STT: Groq Whisper",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=B.CASE_TEAL,
        ).pack(side="right", padx=10)

    # ------------------------------------------------------------------
    def _build_hw_btn_bar(self):
        """
        Physical hardware button row — mimics BMO's actual button layout.

          [🔴 STOP]  [🔵 LISTEN]  [🟢 SEND]  [🟡 MENU]
        """
        bar = ctk.CTkFrame(
            self._main_body,
            height=72,
            fg_color=B.BEZEL,
            corner_radius=0,
        )
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        btn_opts = dict(
            height=48,
            corner_radius=24,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )

        # 🔴 STOP — Button A
        self._stop_btn = ctk.CTkButton(
            bar, text="● STOP",
            fg_color=B.BTN_RED, hover_color=B.BTN_RED_H,
            text_color=B.TEXT_LIGHT,
            command=self._stop_all,
            **btn_opts,
        )
        self._stop_btn.pack(side="left", padx=(18, 6), pady=12, expand=True)

        # 🔵 LISTEN — Button B  (also start-listening)
        self._listen_btn = ctk.CTkButton(
            bar, text="▶ LISTEN",
            fg_color=B.BTN_BLUE, hover_color=B.BTN_BLUE_H,
            text_color=B.TEXT_LIGHT,
            command=self._toggle_listening,
            **btn_opts,
        )
        self._listen_btn.pack(side="left", padx=6, pady=12, expand=True)

        # 🟢 SEND — Button C
        self._send_btn = ctk.CTkButton(
            bar, text="✔ SEND",
            fg_color=B.BTN_GREEN, hover_color=B.BTN_GREEN_H,
            text_color=B.TEXT_LIGHT,
            command=self._on_text_submit,
            **btn_opts,
        )
        self._send_btn.pack(side="left", padx=6, pady=12, expand=True)

        # 🟡 MENU — D-Pad / Settings
        self._menu_btn = ctk.CTkButton(
            bar, text="☰ MENU",
            fg_color=B.BTN_DPAD, hover_color=B.BTN_DPAD_H,
            text_color=B.TEXT_DARK,
            command=self._toggle_drawer,
            **btn_opts,
        )
        self._menu_btn.pack(side="left", padx=(6, 6), pady=12, expand=True)

        # ⏻ QUIT — Shutdown BMO
        self._quit_btn = ctk.CTkButton(
            bar, text="⏻ QUIT",
            fg_color="#2d2d2d", hover_color="#111111",
            text_color="#ff6b6b",
            border_width=2,
            border_color="#ff6b6b",
            command=self._on_close,
            **btn_opts,
        )
        self._quit_btn.pack(side="left", padx=(6, 18), pady=12, expand=True)

    # ══════════════════════════════════════════════════════════════════
    # State change → UI update
    # ══════════════════════════════════════════════════════════════════

    def _on_state_change(self, state: AssistantState):
        color = STATE_COLORS[state]
        label = STATE_LABELS[state]
        self.after(0, self._apply_state_ui, state, color, label)

    # Map AssistantState enum values to face image keys
    _STATE_FACE_MAP = {
        AssistantState.IDLE:      "idle",
        AssistantState.LISTENING: "listen",
        AssistantState.THINKING:  "think",
        AssistantState.SPEAKING:  "speak",
    }

    def _apply_state_ui(self, state: AssistantState, color: str, label: str):
        face_key = self._STATE_FACE_MAP.get(state, "idle")
        self._face.update_state(face_key)
        self._state_label.configure(text=label, text_color=color)
        self._status_lbl.configure(text=label)

        if state == AssistantState.IDLE:
            self._listen_btn.configure(
                text="▶ LISTEN",
                fg_color=B.BTN_BLUE,
                hover_color=B.BTN_BLUE_H,
            )
        elif state == AssistantState.LISTENING:
            self._listen_btn.configure(
                text="⏹ RECORDING",
                fg_color=B.BTN_RED,
                hover_color=B.BTN_RED_H,
            )
        elif state in (AssistantState.THINKING, AssistantState.SPEAKING):
            self._listen_btn.configure(
                text="⌛ BUSY",
                fg_color=B.BTN_DPAD,
                hover_color=B.BTN_DPAD_H,
            )

    # ══════════════════════════════════════════════════════════════════
    # Chat helpers
    # ══════════════════════════════════════════════════════════════════

    def add_message(self, role: str, text: str):
        self.after(0, self._add_message_ui, role, text)

    def _add_message_ui(self, role: str, text: str):
        ts = time.strftime("%H:%M:%S")
        bubble = ChatMessage(self._chat_scroll,
                             role=role, text=text, timestamp=ts)
        bubble.grid(row=self._chat_row, column=0,
                    sticky="ew", padx=6, pady=4)
        self._chat_scroll.columnconfigure(0, weight=1)
        self._chat_row += 1
        self.after(80, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        try:
            self._chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def add_system_message(self, text: str):
        """Small italic system notice (no bubble)."""
        self.after(0, self._add_sys_ui, text)

    def _add_sys_ui(self, text: str):
        lbl = ctk.CTkLabel(
            self._chat_scroll,
            text=f"— {text} —",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color=PALETTE["text_dim"],
        )
        lbl.grid(row=self._chat_row, column=0,
                 sticky="ew", padx=6, pady=2)
        self._chat_row += 1

    def clear_history(self):
        self.conversation.clear()
        for widget in self._chat_scroll.winfo_children():
            widget.destroy()
        self._chat_row = 0
        self.add_system_message("History cleared.")

    # ══════════════════════════════════════════════════════════════════
    # Drawer toggle
    # ══════════════════════════════════════════════════════════════════

    def _toggle_drawer(self):
        if self._drawer_open:
            self._drawer.pack_forget()
            self._drawer_open = False
        else:
            self._drawer.pack(side="right", fill="y",
                              in_=self._root_frame)
            self._drawer_open = True

    # ══════════════════════════════════════════════════════════════════
    # Style helpers
    # ══════════════════════════════════════════════════════════════════

    def _apply_custom_styles(self):
        pass   # all styling is inline; no extra ttk needed

    # ══════════════════════════════════════════════════════════════════
    # Voice pipeline
    # ══════════════════════════════════════════════════════════════════

    def _toggle_listening(self):
        state = self.state_machine.state
        if state == AssistantState.IDLE:
            self._start_wake_or_record()
        else:
            self._stop_all()

    def _start_wake_or_record(self):
        """Start wake-word listener, or go straight to STT."""
        if self.config.get("wake_word.enabled", True):
            self._start_wake_listener()
        else:
            self._record_and_process()

    def _start_wake_listener(self):
        self.state_machine.transition(AssistantState.LISTENING)
        word = self.config.wake_word

        def _on_wake():
            log.info("Wake word detected — starting STT.")
            self._record_and_process()

        self.wake_detector = WakeWordDetector(
            config=self.config,
            on_detected=_on_wake,
        )
        self.wake_detector.start()

    def _stop_all(self):
        if self.wake_detector:
            self.wake_detector.stop()
            self.wake_detector = None
        self.tts.stop()
        self.state_machine.force(AssistantState.IDLE)

    def _record_and_process(self):
        def worker():
            self.state_machine.force(AssistantState.LISTENING)
            max_dur = self.config.get("audio.command_listen_duration", 10)
            text = self.stt.listen_and_transcribe(max_duration=max_dur)

            if not text:
                self.add_system_message("Could not transcribe — please try again.")
                self.state_machine.force(AssistantState.IDLE)
                return

            self.add_message("user", text)
            self.conversation.add_user(text)

            self.state_machine.force(AssistantState.THINKING)
            history = self.conversation.get_for_llm()
            response_chunks = []

            for token in self.llm.chat(history, text):
                response_chunks.append(token)

            full_response = "".join(response_chunks).strip()
            if full_response:
                self.conversation.add_assistant(full_response)
                self.add_message("assistant", full_response)
                self.state_machine.force(AssistantState.SPEAKING)
                self.tts.speak(full_response)

            self.state_machine.force(AssistantState.IDLE)

        self._active_worker = threading.Thread(
            target=worker, daemon=True, name="VoicePipeline")
        self._active_worker.start()

    # ══════════════════════════════════════════════════════════════════
    # Text input
    # ══════════════════════════════════════════════════════════════════

    def _on_text_submit(self, event=None):
        text = self._text_entry.get().strip()
        if not text:
            return
        self._text_entry.delete(0, "end")

        def worker():
            self.add_message("user", text)
            self.conversation.add_user(text)
            self.state_machine.force(AssistantState.THINKING)
            history = self.conversation.get_for_llm()
            response_chunks = []

            for token in self.llm.chat(history, text):
                response_chunks.append(token)

            full_response = "".join(response_chunks).strip()
            if full_response:
                self.conversation.add_assistant(full_response)
                self.add_message("assistant", full_response)
                self.state_machine.force(AssistantState.SPEAKING)
                self.tts.speak(full_response)

            self.state_machine.force(AssistantState.IDLE)

        self._active_worker = threading.Thread(
            target=worker, daemon=True, name="TextPipeline")
        self._active_worker.start()

    def _manual_input(self):
        self._text_entry.focus()

    # ══════════════════════════════════════════════════════════════════
    # Shutdown
    # ══════════════════════════════════════════════════════════════════

    def _on_close(self):
        log.info("Shutting down…")
        self._stop_all()
        self.conversation.save()
        self.destroy()
