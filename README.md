# HAKA Voice Assistant v4

> A production-grade, modular voice assistant with a cyberpunk dark-mode GUI.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Groq API key to .env
#    Edit .env and replace the placeholder value

# 3. Run
python main.py
```

## Project Structure

```
my_assistant_v4/
├── assets/               # Icons, sounds
├── docs/                 # All documentation
├── src/
│   ├── core/
│   │   ├── stt.py        # Groq Whisper STT (with failover)
│   │   ├── llm.py        # Ollama LLM (devstral-small-2:24b-cloud)
│   │   ├── tts.py        # Multi-engine TTS
│   │   └── wake.py       # Wake word detection
│   ├── ui/
│   │   └── app.py        # CustomTkinter cyberpunk GUI
│   └── utils/
│       ├── config.py     # Config loader (.env + config.json)
│       ├── conversation.py  # Chat history manager
│       ├── logger.py     # Colorized logging
│       └── state_machine.py  # IDLE/LISTENING/THINKING/SPEAKING
├── tests/
│   └── test_stt_and_state.py
├── sessions/             # Auto-saved conversation sessions
├── logs/                 # Log files
├── config.json
├── .env                  # Your API keys (never commit!)
├── requirements.txt
└── main.py
```

## Keyboard Shortcuts

| Shortcut     | Action                         |
|--------------|--------------------------------|
| `Ctrl+L`     | Toggle wake word listening     |
| `Ctrl+D`     | Clear conversation history     |
| `Ctrl+,`     | Open/close settings drawer     |
| `Escape`     | Stop all activity              |
| `Enter`      | Send typed message             |

## State Machine

```
IDLE ──→ LISTENING ──→ THINKING ──→ SPEAKING ──→ IDLE
           ↑                                        │
           └────────────────────────────────────────┘
                    (auto-restart after response)
```

## Groq Failover Logic

The STT engine uses a critical failover:
1. Transcribe with `whisper-large-v3` (primary)  
2. On `RateLimitError` (HTTP 429) → automatically retry with `whisper-large-v3-turbo`

## Configuration

Edit `config.json` to change:
- Wake word (`wake_word.word`)
- Ollama model (`ollama.model`) — default: `devstral-small-2:24b-cloud`
- TTS engine (`tts.engine`) — `pyttsx3`, `gtts`, or `edge`
- Language (`language.code`)

## Running Tests

```bash
python -m pytest tests/ -v
```
