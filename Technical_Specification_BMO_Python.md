# Technical Specification: Project BMO/HAKA (Python Version)

**Document Version:** 1.0  
**Date:** February 21, 2026  
**Purpose:** Technical handover for React.js + Node.js rewrite  
**Original Stack:** Python 3.x + CustomTkinter + Groq + Ollama

---

## Executive Summary

BMO (also known as HAKA) is a production-grade voice assistant featuring a BMO-themed GUI with animated face expressions, wake word detection, speech-to-text (STT), large language model (LLM) integration, and text-to-speech (TTS). The system uses an asynchronous state machine pattern with event-driven UI updates to manage the voice interaction pipeline.

---

## 1. High-Level Architecture View

### Architecture Pattern
**Asynchronous State Machine + Event-Driven GUI + Observer Pattern**

The system follows a clear separation between:
- **Backend Logic** (`src/core/` + `src/utils/`) - Handles all AI processing, audio I/O, and state management
- **Frontend UI** (`src/ui/`) - CustomTkinter-based GUI that observes state changes and updates visuals

### Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (src/ui/)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AssistantApp (main window)                          │   │
│  │  - Subscribes to StateMachine                        │   │
│  │  - Renders FaceWidget + Chat + Controls              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ (Observer callbacks)
┌─────────────────────────────────────────────────────────────┐
│              Core Logic Layer (src/core/)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  StateMachine (state_machine.py)                     │   │
│  │  - Manages IDLE → LISTENING → THINKING → SPEAKING    │   │
│  │  - Notifies observers on state transitions           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │   STT   │  │   LLM   │  │   TTS   │  │  Wake   │      │
│  │ (Groq)  │  │(Ollama) │  │(Multi)  │  │  Word   │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Key Communication Mechanism
- **Observer Pattern**: UI subscribes to `StateMachine` via `subscribe(callback)`
- **Thread Safety**: All state transitions use threading locks
- **Async Execution**: Voice pipeline runs in daemon threads to keep UI responsive
- **Event Loop**: CustomTkinter's `mainloop()` handles UI updates via `after()` calls



---

## 2. Current Project Structure & Responsibilities

### Directory Layout

```
my_assistant_v4/
├── main.py                    # Entry point - initializes Config and AssistantApp
├── config.json                # All configuration settings (API, models, UI)
├── .env                       # Environment variables (GROQ_API_KEY)
├── requirements.txt           # Python dependencies
│
├── assets/
│   └── faces/                 # 5 PNG images for BMO face expressions
│       ├── idle.png           # Default resting face
│       ├── listen.png         # Recording/listening expression
│       ├── think.png          # Processing/thinking expression
│       ├── speak.png          # Speaking/responding expression
│       └── error.png          # Error state expression
│
├── src/
│   ├── core/                  # Backend AI/Audio engines
│   │   ├── stt.py             # Speech-to-Text (Groq Whisper with failover)
│   │   ├── llm.py             # LLM integration (Ollama streaming)
│   │   ├── tts.py             # Text-to-Speech (pyttsx3/gTTS/Edge)
│   │   └── wake.py            # Wake word detection (SpeechRecognition)
│   │
│   ├── ui/                    # Frontend GUI components
│   │   ├── app.py             # Main window (AssistantApp class)
│   │   └── face_widget.py     # Animated BMO face component
│   │
│   └── utils/                 # Shared utilities
│       ├── config.py          # Config loader + BMO_Body color constants
│       ├── conversation.py    # Chat history manager
│       ├── logger.py          # Colorized logging setup
│       ├── paths.py           # Path resolution (PyInstaller-aware)
│       └── state_machine.py   # Thread-safe state manager
│
├── sessions/                  # Auto-saved conversation JSON files
├── logs/                      # Application log files
└── tests/                     # Unit tests
```

### Module Responsibilities

#### Core Modules (`src/core/`)

**`stt.py` - Speech-to-Text Engine**
- Records audio from microphone using `sounddevice`
- Implements Voice Activity Detection (VAD) for silence detection
- Sends audio to Groq Whisper API with critical failover mechanism
- Manages temporary WAV file creation and cleanup

**`llm.py` - Large Language Model Engine**
- Connects to local Ollama server (default: `http://localhost:11434`)
- Streams LLM responses token-by-token for real-time display
- Supports runtime model switching via `set_model()`
- Queries available models via `list_ollama_models()`

**`tts.py` - Text-to-Speech Engine**
- Multi-engine support: pyttsx3 (offline), gTTS (online), Edge TTS (Microsoft)
- Runs audio playback in background threads to avoid UI blocking
- Supports speed adjustment (slow/normal/fast)
- Handles temporary audio file cleanup

**`wake.py` - Wake Word Detector**
- Continuously listens in 3-second bursts
- Uses Google Web Speech API via `speech_recognition` library
- Runs in daemon thread, calls callback when wake word detected
- Configurable wake word (default: "hi")

#### UI Modules (`src/ui/`)

**`app.py` - Main Application Window (AssistantApp)**
- CustomTkinter-based GUI styled like BMO device
- Manages all UI components: face, chat log, buttons, settings drawer
- Subscribes to StateMachine and updates UI on state changes
- Orchestrates voice pipeline in worker threads
- Handles keyboard shortcuts (Ctrl+L, Ctrl+D, Esc, etc.)

**`face_widget.py` - Animated Face Component (FaceWidget)**
- Loads 5 PNG images from `assets/faces/`
- Displays appropriate face based on current state
- Implements speaking animation (toggles between speak/idle images)
- Size: 200x150 pixels

#### Utility Modules (`src/utils/`)

**`state_machine.py` - State Manager (StateMachine)**
- Defines 4 states: IDLE, LISTENING, THINKING, SPEAKING
- Enforces valid state transitions (e.g., IDLE → LISTENING only)
- Thread-safe using `threading.Lock()`
- Implements observer pattern for UI notifications

**`config.py` - Configuration Manager (Config)**
- Loads `.env` for secrets (GROQ_API_KEY)
- Loads `config.json` for all settings
- Provides dot-notation access: `config.get("ollama.model")`
- Defines `BMO_Body` class with official color constants

**`conversation.py` - Chat History Manager (ConversationManager)**
- Maintains rolling conversation history (default: last 10 exchanges)
- Saves sessions to JSON files with timestamps
- Trims old messages to fit LLM context window
- Formats history for LLM API consumption

**`logger.py` - Logging Setup**
- Configures colorized console output
- Writes to daily log files in `logs/` directory
- Per-module loggers with consistent formatting

**`paths.py` - Path Resolution**
- PyInstaller-aware path resolution (handles `_MEIPASS`)
- Ensures assets load correctly in both dev and compiled exe

