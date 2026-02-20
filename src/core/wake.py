"""
Wake Word Detection (src/core/wake.py)

Uses local SpeechRecognition (Google Web Speech API) to detect the
configured wake word. Runs in a background thread and calls a callback
when the word is heard.
"""
import os
import wave
import threading
import time
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import speech_recognition as sr

from src.utils.logger import get_logger
from src.utils.config import Config

log = get_logger("wake")


class WakeWordDetector:
    """
    Continuously listens in short bursts for the configured wake word.
    Non-blocking: runs in its own daemon thread.
    """

    def __init__(self, config: Config, on_detected: Callable[[], None]):
        self.config = config
        self.on_detected = on_detected
        self.recognizer = sr.Recognizer()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Start the wake word listener thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WakeWordThread"
        )
        self._thread.start()
        log.info(f"Wake word listener started — listening for '{self.config.wake_word}'")

    def stop(self):
        """Signal the listener thread to stop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        log.info("Wake word listener stopped.")

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _loop(self):
        sample_rate = self.config.get("audio.sample_rate", 16000)
        duration = self.config.get("wake_word.wake_word_listen_duration", 3)
        language = self.config.language
        wake_word = self.config.wake_word.lower()

        while not self._stop_event.is_set():
            temp_path = None
            try:
                # Record a short burst
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype=np.int16,
                )
                sd.wait()

                if self._stop_event.is_set():
                    break

                # Save to temp wav
                temp_path = f"_wake_{int(time.time())}.wav"
                with wave.open(temp_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data.tobytes())

                # Transcribe locally
                with sr.AudioFile(temp_path) as source:
                    audio = self.recognizer.record(source)

                text = self.recognizer.recognize_google(
                    audio, language=language
                ).lower()
                log.debug(f"Wake heard: '{text}'")

                if wake_word in text:
                    log.info(f"✅ Wake word '{wake_word}' detected!")
                    self._stop_event.set()   # pause self before callback
                    self.on_detected()

            except sr.UnknownValueError:
                pass  # Silence or unintelligible — normal
            except sr.RequestError as e:
                log.warning(f"Speech recognition request error: {e}")
                time.sleep(2)
            except Exception as e:
                log.error(f"Wake word loop error: {e}")
                time.sleep(1)
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
