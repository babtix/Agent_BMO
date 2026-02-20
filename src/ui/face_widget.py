"""
FaceWidget — BMO-style animated face display.

Loads 5 face images from assets/faces/ and swaps them based on the
current AssistantState.  Provides a simple speaking-animation toggle
that alternates between the "speak" and "idle" images.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from PIL import Image

from src.utils.logger import get_logger

log = get_logger("face_widget")

# Resolve the assets/faces/ directory relative to this file
_FACES_DIR = Path(__file__).resolve().parents[2] / "assets" / "faces"

# Map logical state names → image filenames (without extension)
_STATE_IMAGE_MAP = {
    "idle":    "idle",
    "listen":  "listen",
    "think":   "think",
    "speak":   "speak",
    "error":   "error",
}

# Display size for the face images (width, height)
FACE_SIZE = (200, 150)


class FaceWidget(ctk.CTkFrame):
    """
    A CTkFrame that shows one of 5 BMO face images depending on the
    current assistant state.

    Usage
    -----
        face = FaceWidget(parent, fg_color="#D4EAC8")
        face.pack(pady=20)
        face.update_state("idle")
        face.animate_speak(True)   # start mouth toggle
        face.animate_speak(False)  # stop mouth toggle
    """

    _SPEAK_TOGGLE_MS = 400  # ms between speak/idle frames

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)

        # --- Load and resize images ----------------------------------------
        self._images: dict[str, ctk.CTkImage] = {}
        for state_key, filename in _STATE_IMAGE_MAP.items():
            img_path = _FACES_DIR / f"{filename}.png"
            if img_path.exists():
                pil_img = Image.open(img_path)
                self._images[state_key] = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=FACE_SIZE,
                )
                log.debug("Loaded face image: %s", img_path)
            else:
                log.warning("Face image not found: %s", img_path)

        # --- Central label (displays the face image) -----------------------
        self._label = ctk.CTkLabel(
            self,
            text="",
            image=self._images.get("idle"),
            fg_color="transparent",
        )
        self._label.pack(expand=True)

        # --- State tracking ------------------------------------------------
        self._current_state: str = "idle"
        self._speaking: bool = False
        self._speak_job: Optional[str] = None
        self._speak_frame: bool = False  # toggles between speak/idle

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_state(self, state: str) -> None:
        """
        Set the displayed face image.

        Parameters
        ----------
        state : str
            One of "idle", "listen", "think", "speak", "error".
        """
        state = state.lower()
        self._current_state = state

        img = self._images.get(state)
        if img is not None:
            self._label.configure(image=img)
        else:
            log.warning("No image for state '%s'", state)

        # Auto-start / stop speak animation
        if state == "speak":
            self.animate_speak(True)
        else:
            self.animate_speak(False)

    def animate_speak(self, is_speaking: bool) -> None:
        """
        Toggle the speaking mouth animation.

        When *is_speaking* is True the widget alternates between the
        "speak" and "idle" face images every ``_SPEAK_TOGGLE_MS`` ms.
        """
        if is_speaking and not self._speaking:
            self._speaking = True
            self._speak_frame = False
            self._tick_speak()
        elif not is_speaking and self._speaking:
            self._speaking = False
            if self._speak_job is not None:
                self.after_cancel(self._speak_job)
                self._speak_job = None
            # Restore the current-state image
            img = self._images.get(self._current_state)
            if img:
                self._label.configure(image=img)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tick_speak(self) -> None:
        """Alternate between speak and idle images."""
        if not self._speaking:
            return

        self._speak_frame = not self._speak_frame
        key = "speak" if self._speak_frame else "idle"
        img = self._images.get(key)
        if img:
            self._label.configure(image=img)

        self._speak_job = self.after(self._SPEAK_TOGGLE_MS, self._tick_speak)
