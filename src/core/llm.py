"""
LLM Engine (src/core/llm.py)

Interacts with Ollama using a configurable model.
Default: devstral-small-2:24b-cloud
Supports streaming token generation and runtime model switching.
"""
from typing import Generator, List, Dict, Optional

import ollama

from src.utils.logger import get_logger
from src.utils.config import Config

log = get_logger("llm")

DEFAULT_MODEL = "devstral-small-2:24b-cloud"


def list_ollama_models() -> List[str]:
    """
    Fetch the list of locally available Ollama models.
    Returns a list of model name strings, or an empty list on error.
    """
    try:
        response = ollama.list()
        # The response object has a .models attribute (list of Model objects)
        models = response.models if hasattr(response, "models") else response.get("models", [])
        names = []
        for m in models:
            # Each item is an ollama.ModelInfo object with a .model attribute
            if hasattr(m, "model"):
                names.append(m.model)
            elif isinstance(m, dict):
                names.append(m.get("name") or m.get("model", ""))
        names = [n for n in names if n]
        log.info(f"Found {len(names)} Ollama model(s): {names}")
        return names
    except Exception as e:
        log.error(f"Could not fetch Ollama model list: {e}")
        return []


class LLMEngine:
    """
    Sends conversation history to Ollama and streams the response.
    Model can be switched at runtime via set_model().
    """

    def __init__(self, config: Config):
        self.config = config
        self.model: str = config.ollama_model or DEFAULT_MODEL
        self.host: str = config.ollama_host
        self.temperature: float = config.get("ollama.temperature", 0.7)
        self.system_prompt: str = config.get(
            "conversation.system_prompt",
            "You are a helpful voice assistant. Keep responses concise and natural.",
        )
        log.info(f"LLM Engine initialised — model: {self.model}")

    # ------------------------------------------------------------------
    # Runtime model switching
    # ------------------------------------------------------------------

    def set_model(self, model_name: str):
        """Switch the active Ollama model at runtime and persist to config."""
        self.model = model_name
        self.config.set("ollama.model", model_name)
        log.info(f"LLM model switched to: {model_name}")

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def chat(
        self,
        history: List[Dict[str, str]],
        user_message: str,
    ) -> Generator[str, None, None]:
        """
        Stream the assistant response token-by-token.

        Yields:
            str: Each token chunk as it arrives from Ollama.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        log.info(f"Sending {len(messages)} messages to Ollama ({self.model})…")

        try:
            stream = ollama.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={"temperature": self.temperature},
            )
            for chunk in stream:
                token = chunk["message"]["content"]
                if token:
                    yield token

        except Exception as e:
            log.error(f"Ollama error: {e}")
            yield f"[Error contacting Ollama: {e}]"

    def chat_blocking(
        self,
        history: List[Dict[str, str]],
        user_message: str,
    ) -> str:
        """Return the full response as a single string (non-streaming)."""
        return "".join(self.chat(history, user_message))
