"""
Config - Loads .env and config.json, provides typed dot-notation access.
Also exposes BMO_Body: the official BMO hardware colour constants.
"""


# ══════════════════════════════════════════════════════════════════════
class BMO_Body:
    """
    Official colours based on the BMO physical enclosure.
    Reference anywhere in the codebase:
        from src.utils.config import BMO_Body
        color = BMO_Body.BTN_RED
    """

    # ── Case & Screen ──────────────────────────────────────────────────
    CASE_TEAL   = "#5F9EA0"   # Outer shell / body colour
    SCREEN_BG   = "#D4EAC8"   # CRT phosphor-green screen background

    # ── Hardware Buttons (mapped to UI semantics) ─────────────────────
    BTN_DPAD    = "#F1C40F"   # Yellow D-Pad  → Menu / Nav
    BTN_RED     = "#FF6B6B"   # Red Button A  → Stop / Cancel / Record
    BTN_BLUE    = "#4ECDC4"   # Blue Button B → Listen / Confirm / Play
    BTN_GREEN   = "#2ECC71"   # Green Button C→ Start / Save / Execute

    # ── Text on BMO surfaces ───────────────────────────────────────────
    TEXT_DARK   = "#2C3E50"   # Deep Navy — text on teal or green
    TEXT_LIGHT  = "#FFFFFF"   # White     — text on coloured buttons

    # ── Derived hover shades (10 % darker) ────────────────────────────
    CASE_TEAL_H  = "#4a7d7f"
    BTN_DPAD_H   = "#c9a00d"
    BTN_RED_H    = "#cc5252"
    BTN_BLUE_H   = "#38a89d"
    BTN_GREEN_H  = "#27ae60"

    # ── Bezel / panel tones ───────────────────────────────────────────
    BEZEL        = "#4a7d7f"   # slightly darker teal for the screen frame
    SURFACE_LT   = "#e8f5e0"   # lighter phosphor green for input fields
    SURFACE_DK   = "#2C3E50"   # Deep Navy for overlays / drawers


# ══════════════════════════════════════════════════════════════════════

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.utils.paths import get_executable_dir
from src.utils.logger import get_logger

log = get_logger("config")

# ROOT for config/secrets should be where the executable lives
ROOT = get_executable_dir()


class Config:
    """Unified configuration manager for v4."""

    def __init__(self):
        # Load .env first so env-vars override defaults
        env_file = ROOT / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            log.info(f"Loaded .env from {env_file}")
        else:
            log.warning(".env file not found — using system environment variables.")

        config_file = ROOT / "config.json"
        if not config_file.exists():
            raise FileNotFoundError(f"config.json not found at {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            self._data: dict = json.load(f)

        log.info("config.json loaded successfully.")

    # ------------------------------------------------------------------
    # Dot-notation access
    # ------------------------------------------------------------------

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get nested value using dot notation, e.g. 'ollama.model'."""
        keys = key_path.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value: Any):
        """Set a nested value and persist to config.json."""
        keys = key_path.split(".")
        node = self._data
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value
        self._save()

    def _save(self):
        config_file = ROOT / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def groq_api_key(self) -> str:
        env_var = self.get("groq.api_key_env", "GROQ_API_KEY")
        key = os.getenv(env_var, "")
        if not key:
            log.error(f"Environment variable '{env_var}' is not set!")
        return key

    @property
    def ollama_model(self) -> str:
        return self.get("ollama.model", "devstral-small-2:24b-cloud")

    @property
    def ollama_host(self) -> str:
        return self.get("ollama.host", "http://localhost:11434")

    @property
    def wake_word(self) -> str:
        return self.get("wake_word.word", "computer")

    @property
    def language(self) -> str:
        return self.get("language.code", "en")

    @property
    def tts_engine(self) -> str:
        return self.get("tts.engine", "pyttsx3")

    @property
    def tts_speed(self) -> str:
        return self.get("tts.speed", "normal")
