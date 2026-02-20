"""
main.py — Entry point for HAKA Voice Assistant v4

Run from the my_assistant_v4/ directory:
    python main.py
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'src' is importable
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.utils.logger import get_logger
from src.utils.config import Config
from src.ui.app import AssistantApp

log = get_logger("main")


def main():
    log.info("=" * 60)
    log.info("  HAKA Voice Assistant v4 — Starting")
    log.info("=" * 60)

    try:
        config = Config()
    except FileNotFoundError as e:
        log.critical(f"Cannot load config: {e}")
        sys.exit(1)

    app = AssistantApp(config)
    app.mainloop()

    log.info("HAKA shut down cleanly. Goodbye.")


if __name__ == "__main__":
    main()
