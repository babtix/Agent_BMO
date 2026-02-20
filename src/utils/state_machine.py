"""
State Machine - Thread-safe state manager for the voice assistant pipeline.

States:
  IDLE      → Waiting for wake word
  LISTENING → Recording user command
  THINKING  → LLM processing
  SPEAKING  → TTS playback
"""
import threading
from enum import Enum, auto
from typing import Callable, List

from src.utils.logger import get_logger

log = get_logger("state_machine")


class AssistantState(Enum):
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()


# Valid state transitions
_TRANSITIONS: dict[AssistantState, List[AssistantState]] = {
    AssistantState.IDLE:      [AssistantState.LISTENING],
    AssistantState.LISTENING: [AssistantState.THINKING, AssistantState.IDLE],
    AssistantState.THINKING:  [AssistantState.SPEAKING, AssistantState.IDLE],
    AssistantState.SPEAKING:  [AssistantState.IDLE, AssistantState.LISTENING],
}


class StateMachine:
    """Thread-safe assistant state machine with observer callbacks."""

    def __init__(self):
        self._state = AssistantState.IDLE
        self._lock = threading.Lock()
        self._observers: List[Callable[[AssistantState], None]] = []

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------

    @property
    def state(self) -> AssistantState:
        with self._lock:
            return self._state

    def transition(self, new_state: AssistantState) -> bool:
        """
        Attempt a state transition. Returns True on success.
        Invalid transitions are logged and rejected.
        """
        with self._lock:
            allowed = _TRANSITIONS.get(self._state, [])
            if new_state not in allowed:
                log.warning(
                    f"Invalid transition: {self._state.name} → {new_state.name}"
                )
                return False
            old = self._state
            self._state = new_state
            log.info(f"State: {old.name} → {new_state.name}")

        # Notify observers OUTSIDE the lock to avoid deadlocks
        self._notify(new_state)
        return True

    def force(self, new_state: AssistantState):
        """Force a state (e.g. on error recovery). Bypasses validation."""
        with self._lock:
            old = self._state
            self._state = new_state
        log.warning(f"Forced state: {old.name} → {new_state.name}")
        self._notify(new_state)

    # ------------------------------------------------------------------
    # Observer pattern
    # ------------------------------------------------------------------

    def subscribe(self, callback: Callable[[AssistantState], None]):
        """Register a listener that fires on every state change."""
        self._observers.append(callback)

    def _notify(self, state: AssistantState):
        for cb in self._observers:
            try:
                cb(state)
            except Exception as e:
                log.error(f"Observer error: {e}")

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def is_idle(self) -> bool:
        return self.state == AssistantState.IDLE

    def is_listening(self) -> bool:
        return self.state == AssistantState.LISTENING

    def is_thinking(self) -> bool:
        return self.state == AssistantState.THINKING

    def is_speaking(self) -> bool:
        return self.state == AssistantState.SPEAKING
