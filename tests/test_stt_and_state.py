"""
tests/test_stt.py — Unit tests for STT failover logic
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSTTFailover(unittest.TestCase):
    """Tests the critical Groq Whisper failover logic."""

    def _make_stt(self, config=None):
        from src.core.stt import STTEngine
        if config is None:
            config = MagicMock()
            config.groq_api_key = "test_key"
            config.language = "en"
            config.get.side_effect = lambda k, d=None: {
                "audio.sample_rate": 16000,
                "audio.channels": 1,
                "audio.silence_threshold": 0.01,
                "audio.silence_duration": 1.5,
            }.get(k, d)
        return STTEngine(config)

    @patch("src.core.stt.Groq")
    def test_primary_model_used_first(self, mock_groq_cls):
        """Should attempt whisper-large-v3 first."""
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "hello world"

        stt = self._make_stt()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", unittest.mock.mock_open(read_data=b"audio")):
            result = stt.transcribe("fake.wav")

        call_args = mock_client.audio.transcriptions.create.call_args
        self.assertEqual(call_args.kwargs["model"], "whisper-large-v3")
        self.assertEqual(result, "hello world")

    @patch("src.core.stt.Groq")
    def test_failover_on_rate_limit(self, mock_groq_cls):
        """On RateLimitError, should retry with whisper-large-v3-turbo."""
        import groq as groq_lib
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client

        # First call raises 429, second succeeds
        mock_client.audio.transcriptions.create.side_effect = [
            groq_lib.RateLimitError("rate limit", response=MagicMock(), body={}),
            "fallback response",
        ]

        stt = self._make_stt()

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", unittest.mock.mock_open(read_data=b"audio")):
            result = stt.transcribe("fake.wav")

        self.assertEqual(mock_client.audio.transcriptions.create.call_count, 2)
        second_call_model = mock_client.audio.transcriptions.create.call_args_list[1].kwargs["model"]
        self.assertEqual(second_call_model, "whisper-large-v3-turbo")
        self.assertEqual(result, "fallback response")


class TestStateMachine(unittest.TestCase):
    """Tests state machine transitions."""

    def setUp(self):
        from src.utils.state_machine import StateMachine, AssistantState
        self.sm = StateMachine()
        self.State = AssistantState

    def test_initial_state_is_idle(self):
        self.assertEqual(self.sm.state, self.State.IDLE)

    def test_valid_transition(self):
        ok = self.sm.transition(self.State.LISTENING)
        self.assertTrue(ok)
        self.assertEqual(self.sm.state, self.State.LISTENING)

    def test_invalid_transition_rejected(self):
        # IDLE → SPEAKING is invalid
        ok = self.sm.transition(self.State.SPEAKING)
        self.assertFalse(ok)
        self.assertEqual(self.sm.state, self.State.IDLE)

    def test_full_pipeline(self):
        self.sm.transition(self.State.LISTENING)
        self.sm.transition(self.State.THINKING)
        self.sm.transition(self.State.SPEAKING)
        self.sm.transition(self.State.IDLE)
        self.assertEqual(self.sm.state, self.State.IDLE)

    def test_observer_notified(self):
        events = []
        self.sm.subscribe(lambda s: events.append(s))
        self.sm.transition(self.State.LISTENING)
        self.assertEqual(events, [self.State.LISTENING])


if __name__ == "__main__":
    unittest.main(verbosity=2)
