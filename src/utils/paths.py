import os
import sys
from pathlib import Path

def get_base_path():
    """Get the base path for assets and config files."""
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in a normal Python environment
        return Path(__file__).resolve().parent.parent.parent

def get_executable_dir():
    """Get the directory where the executable (or script) is located."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent.parent
