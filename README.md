# BMO Agent - Voice Assistant v4

> A production-grade, modular voice assistant with a high-fidelity BMO-themed GUI.

## Introduction

**BMO Agent** is a state-of-the-art voice assistant modeled after the iconic BMO device. It features a custom FaceWidget that changes expressions based on its internal state, a robust asynchronous pipeline, and a modular architecture designed for stability and extensibility.

## Features

- **BMO-Themed UI**: A beautiful `CustomTkinter` interface styled like the physical BMO device.
- **Dynamic FaceWidget**: Real-time expression changes (Idle, Listen, Think, Speak, Error) based on the assistant's state.
- **Advanced State Machine**: Thread-safe management of IDLE, LISTENING, THINKING, and SPEAKING states.
- **Multi-Engine Pipeline**:
  - **STT**: Groq Whisper with automatic failover logic.
  - **LLM**: Local Ollama support (defaults to `qwen3-coder:480b-cloud`).
  - **TTS**: Support for `pyttsx3` (Offline), `gTTS` (Online), and `Edge TTS` (Microsoft).
- **Physical-Style Controls**: A hardware-style button bar for manual interaction.
- **Session Persistence**: Automatic saving of conversation logs to the `sessions/` directory.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Groq API key to .env
#    Edit .env and replace the placeholder value

# 3. Ensure Ollama is running locally

# 4. Run
python main.py
```

## Project Structure

```
my_assistant_v4/
├── assets/               # BMO face images (idle, listen, think, speak, error)
├── docs/                 # Detailed documentation and design specs
├── src/
│   ├── core/
│   │   ├── stt.py        # Groq Whisper STT (with failover)
│   │   ├── llm.py        # Ollama LLM integration
│   │   ├── tts.py        # Multi-engine TTS (pyttsx3, gTTS, Edge)
│   │   └── wake.py       # Wake word detection
│   ├── ui/
│   │   ├── app.py        # BMO-style Main Window
│   │   └── face_widget.py # Animated BMO face component
│   └── utils/
│       ├── config.py     # Config loader (.env + config.json)
│       ├── conversation.py  # Chat history manager
│       ├── logger.py     # Colorized logging
│       └── state_machine.py  # Thread-safe pipeline manager
├── tests/
│   └── test_stt_and_state.py
├── sessions/             # Auto-saved conversation sessions
├── logs/                 # Log files
├── config.json
├── .env                  # Your API keys (never commit!)
├── requirements.txt
└── main.py
```

## Hardware Controls & Shortcuts

The BMO interface features a physical-style button bar:

- **● STOP**: Cancels current action and returns to IDLE.
- **▶ LISTEN**: Toggles voice recording/wake-word detection.
- **✔ SEND**: Submits the text typed in the entry bar.
- **☰ MENU**: Opens the settings drawer.
- **⏻ QUIT**: Shuts down BMO cleanly.

| Shortcut     | Action                         |
|--------------|--------------------------------|
| `Ctrl+L`     | Toggle listening               |
| `Ctrl+D`     | Clear conversation history     |
| `Ctrl+,`     | Open/close settings drawer     |
| `Escape`     | Stop all activity              |
| `Enter`      | Send typed message             |

## Groq Failover Logic

The STT engine preserves the critical v3 failover logic:
1. Transcribe with `whisper-large-v3` (primary).
2. On `RateLimitError` (HTTP 429) → automatically retry with `whisper-large-v3-turbo`.

## Configuration

Edit `config.json` to change:
- Wake word (`wake_word.word`) - e.g., "BMO".
- Ollama model (`ollama.model`).
- TTS engine (`tts.engine`) — `pyttsx3`, `gtts`, or `edge`.

## Running Tests

```bash
python -m pytest tests/ -v
```
