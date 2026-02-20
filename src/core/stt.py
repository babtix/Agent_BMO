"""
STT — Speech-to-Text (src/core/stt.py)

Groq Whisper transcription with CRITICAL failover logic:
  1. Try whisper-large-v3 (primary)
  2. On RateLimitError (HTTP 429) → retry with whisper-large-v3-turbo (fallback)
"""
import os
import wave
import time
import threading
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
import groq

from groq import Groq

from src.utils.logger import get_logger
from src.utils.config import Config

log = get_logger("stt")

PRIMARY_MODEL = "whisper-large-v3"
FALLBACK_MODEL = "whisper-large-v3-turbo"


class STTEngine:
    """
    Records user audio (with optional VAD silence detection) and
    transcribes it via the Groq Whisper API.
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = Groq(api_key=config.groq_api_key)
        self.sample_rate = config.get("audio.sample_rate", 16000)
        self.channels = config.get("audio.channels", 1)
        self.silence_threshold = config.get("audio.silence_threshold", 0.01)
        self.silence_duration = config.get("audio.silence_duration", 1.5)
        self._recording = False

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_command(self, max_duration: int = 10) -> Optional[str]:
        """
        Record until silence or max_duration. Returns path to temp WAV file.
        """
        log.info(f"Recording command (max {max_duration}s)…")
        chunks = []
        silence_chunks = 0
        max_silence = int(self.silence_duration * self.sample_rate / 1024)
        self._recording = True
        start = time.time()

        def callback(indata, frames, time_info, status):
            nonlocal silence_chunks
            chunks.append(indata.copy())
            volume = np.abs(indata).mean()
            if volume < self.silence_threshold:
                silence_chunks += 1
            else:
                silence_chunks = 0

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                blocksize=1024,
                dtype=np.float32,
            ):
                while self._recording:
                    if silence_chunks >= max_silence:
                        log.debug("Silence detected — stopping recording.")
                        break
                    if time.time() - start > max_duration:
                        log.debug("Max duration reached — stopping recording.")
                        break
                    sd.sleep(50)
        except Exception as e:
            log.error(f"Recording error: {e}")
            return None
        finally:
            self._recording = False

        if not chunks:
            log.warning("No audio data recorded.")
            return None

        audio_data = np.concatenate(chunks, axis=0)
        temp_path = f"_cmd_{int(time.time())}.wav"
        self._save_wav(audio_data, temp_path)
        return temp_path

    def stop_recording(self):
        self._recording = False

    def _save_wav(self, data: np.ndarray, path: str):
        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((data * 32767).astype(np.int16).tobytes())

    # ------------------------------------------------------------------
    # Transcription — CRITICAL failover logic preserved from v3
    # ------------------------------------------------------------------

    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcribe an audio file via Groq Whisper.

        Failover logic (CRITICAL):
          1. Attempt with whisper-large-v3
          2. If RateLimitError (429) → log warning, retry with whisper-large-v3-turbo
        """
        if not os.path.exists(audio_path):
            log.error(f"Audio file not found: {audio_path}")
            return None

        language = self.config.language

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        # ── Step 1: Try primary model ──────────────────────────────────
        try:
            log.info(f"Transcribing with {PRIMARY_MODEL}…")
            result = self.client.audio.transcriptions.create(
                file=(audio_path, audio_bytes),
                model=PRIMARY_MODEL,
                response_format="text",
                language=language,
            )
            text = result.strip() if isinstance(result, str) else str(result).strip()
            log.info(f"Transcription OK ({PRIMARY_MODEL}): '{text[:80]}'")
            return text

        except groq.RateLimitError:
            # ── Step 2: Failover to turbo model ───────────────────────
            log.warning(
                f"Rate limit hit on {PRIMARY_MODEL} — "
                f"retrying with {FALLBACK_MODEL}…"
            )
            try:
                result = self.client.audio.transcriptions.create(
                    file=(audio_path, audio_bytes),
                    model=FALLBACK_MODEL,
                    response_format="text",
                    language=language,
                )
                text = result.strip() if isinstance(result, str) else str(result).strip()
                log.info(f"Transcription OK ({FALLBACK_MODEL}): '{text[:80]}'")
                return text
            except Exception as e2:
                log.error(f"Fallback transcription failed: {e2}")
                return None

        except Exception as e:
            log.error(f"Transcription error: {e}")
            return None

    # ------------------------------------------------------------------
    # Convenience: record + transcribe in one call
    # ------------------------------------------------------------------

    def listen_and_transcribe(
        self,
        max_duration: int = 10,
        on_done: Optional[Callable[[Optional[str]], None]] = None,
    ) -> Optional[str]:
        """
        Blocking: record then transcribe.
        Pass on_done callback for async usage.
        """
        audio_path = self.record_command(max_duration)
        if not audio_path:
            if on_done:
                on_done(None)
            return None

        text = self.transcribe(audio_path)

        # Cleanup
        try:
            os.remove(audio_path)
        except OSError:
            pass

        if on_done:
            on_done(text)
        return text
