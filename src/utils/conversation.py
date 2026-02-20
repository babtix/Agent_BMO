"""
Conversation Manager (src/utils/conversation.py)

Manages the rolling message history for the LLM context window.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.logger import get_logger
from src.utils.config import Config

log = get_logger("conversation")

ROOT = Path(__file__).parent.parent.parent


class ConversationManager:
    """Handles chat history, session persistence, and context trimming."""

    def __init__(self, config: Config):
        self.config = config
        self.max_history: int = config.get("conversation.max_history", 10)
        self.save_sessions: bool = config.get("conversation.save_sessions", True)
        session_dir = config.get("conversation.session_dir", "sessions")
        self.session_dir = ROOT / session_dir
        self.session_dir.mkdir(exist_ok=True)

        self.history: List[Dict[str, str]] = []
        self.session_id: Optional[str] = None
        self.session_start: Optional[datetime] = None

    # ------------------------------------------------------------------

    def start_session(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now()
        self.history = []
        log.info(f"Session started: {self.session_id}")

    def add_user(self, text: str):
        self._add("user", text)

    def add_assistant(self, text: str):
        self._add("assistant", text)

    def _add(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # Trim oldest pair if over limit
        pair_limit = self.max_history * 2
        if len(self.history) > pair_limit:
            self.history = self.history[-pair_limit:]

    def get_for_llm(self) -> List[Dict[str, str]]:
        """Return history stripped of timestamps (for LLM API)."""
        return [{"role": m["role"], "content": m["content"]} for m in self.history]

    def clear(self):
        self.history = []
        log.info("History cleared.")

    # ------------------------------------------------------------------

    def save(self):
        if not self.save_sessions or not self.session_id:
            return
        data = {
            "session_id": self.session_id,
            "start": self.session_start.isoformat() if self.session_start else None,
            "end": datetime.now().isoformat(),
            "messages": self.history,
        }
        path = self.session_dir / f"session_{self.session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info(f"Session saved: {path}")
