"""
TTS Engine (src/core/tts.py)

Multi-engine Text-to-Speech supporting pyttsx3, gTTS, and Edge TTS.
Runs audio playback in a background thread so the UI stays responsive.
"""
import os
import time
import threading
import asyncio
from typing import Optional, Callable

from src.utils.logger import get_logger
from src.utils.config import Config

log = get_logger("tts")

# Optional engine imports
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    log.warning("pyttsx3 not installed — offline TTS unavailable.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    log.warning("gTTS not installed.")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    log.warning("edge-tts not installed.")

# Edge TTS voice map
EDGE_VOICES = {
    "en": "en-US-AriaNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
}


class TTSEngine:
    """
    Manages TTS playback with hot-swappable engines.
    All public methods are non-blocking by default (run in daemon threads).
    """

    def __init__(self, config: Config):
        self.config = config
        self.engine_name: str = config.tts_engine
        self.language: str = config.language
        self.speed: str = config.tts_speed
        self._pyttsx3_engine = None
        self._lock = threading.Lock()
        self._active_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._init_pyttsx3()
        log.info(f"TTS Engine: {self.engine_name}")

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_pyttsx3(self):
        if self.engine_name == "pyttsx3" and PYTTSX3_AVAILABLE:
            self._pyttsx3_engine = pyttsx3.init()
            rate = self._pyttsx3_engine.getProperty("rate")
            if self.speed == "slow":
                self._pyttsx3_engine.setProperty("rate", max(80, rate - 50))
            elif self.speed == "fast":
                self._pyttsx3_engine.setProperty("rate", rate + 50)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speak(
        self,
        text: str,
        on_done: Optional[Callable[[], None]] = None,
        blocking: bool = False,
    ):
        """
        Speak the given text.
        Non-blocking by default — passes control back immediately.
        """
        if not text or not text.strip():
            return

        self._stop_flag.clear()

        if blocking:
            self._speak_internal(text, on_done)
        else:
            t = threading.Thread(
                target=self._speak_internal,
                args=(text, on_done),
                daemon=True,
                name="TTSThread",
            )
            self._active_thread = t
            t.start()

    def stop(self):
        """Interrupt current TTS playback."""
        self._stop_flag.set()
        if self.engine_name == "pyttsx3" and self._pyttsx3_engine:
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass

    def set_engine(self, engine_name: str):
        """Hot-swap TTS engine at runtime."""
        self.engine_name = engine_name
        self.config.set("tts.engine", engine_name)
        self._pyttsx3_engine = None
        self._init_pyttsx3()
        log.info(f"TTS engine switched to: {engine_name}")

    def set_speed(self, speed: str):
        """Change TTS speed ('slow', 'normal', 'fast')."""
        self.speed = speed
        self.config.set("tts.speed", speed)
        self._pyttsx3_engine = None
        self._init_pyttsx3()

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _speak_internal(self, text: str, on_done: Optional[Callable]):
        try:
            if self.engine_name == "pyttsx3" and PYTTSX3_AVAILABLE and self._pyttsx3_engine:
                self._speak_pyttsx3(text)
            elif self.engine_name == "edge" and EDGE_TTS_AVAILABLE:
                self._speak_edge(text)
            elif GTTS_AVAILABLE:
                self._speak_gtts(text)
            else:
                log.error("No TTS engine available!")
        except Exception as e:
            log.error(f"TTS error: {e}")
        finally:
            if on_done:
                on_done()

    def _speak_pyttsx3(self, text: str):
        with self._lock:
            engine = self._pyttsx3_engine
            if engine and not self._stop_flag.is_set():
                engine.say(text)
                engine.runAndWait()

    def _speak_gtts(self, text: str):
        try:
            slow = self.speed == "slow"
            tts = gTTS(text=text, lang=self.language, slow=slow)
            path = f"_tts_{int(time.time())}.mp3"
            tts.save(path)
            if not self._stop_flag.is_set():
                os.startfile(path)
                words = len(text.split())
                wpm = 100 if slow else 150
                duration = max(2, (words / wpm) * 60 + 1)
                time.sleep(duration)
            try:
                os.remove(path)
            except OSError:
                pass
        except Exception as e:
            log.error(f"gTTS error: {e}")

    def _speak_edge(self, text: str):
        try:
            path = f"_tts_{int(time.time())}.mp3"
            voice = EDGE_VOICES.get(self.language, "en-US-AriaNeural")
            asyncio.run(self._edge_async(text, voice, path))
            if not self._stop_flag.is_set() and os.path.exists(path):
                os.startfile(path)
                words = len(text.split())
                duration = max(2, (words / 150) * 60 + 1)
                time.sleep(duration)
            try:
                os.remove(path)
            except OSError:
                pass
        except Exception as e:
            log.error(f"Edge TTS error: {e}")

    @staticmethod
    async def _edge_async(text: str, voice: str, path: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)

    def cleanup(self):
        """Release resources."""
        self.stop()
        for f in os.listdir("."):
            if f.startswith("_tts_") and f.endswith(".mp3"):
                try:
                    os.remove(f)
                except OSError:
                    pass
