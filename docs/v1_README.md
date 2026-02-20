# Voice-to-Voice AI System

Two Python scripts for voice interaction with AI:

## 1. main.py - Single Interaction Voice AI

Simple one-shot voice interaction: Record → Transcribe → Think → Speak

### Usage:
```cmd
python main.py
```

Speak after "Recording..." appears. The system will auto-stop after 2 seconds of silence.

---

## 2. assistant.py - Continuous Voice Assistant

Continuous voice assistant with 4-state machine: **WAIT → LISTEN → THINK → SPEAK**

### State Machine:
1. **WAIT**: Listens for wake word ("computer") - processed locally
2. **LISTEN**: Records your command after wake word detected
3. **THINK**: Sends to Ollama LLM (rnj-1:8b-cloud)
4. **SPEAK**: Responds with TTS and loops back to WAIT

### Usage:
```cmd
python assistant.py
```

Say "computer" (or your custom wake word) to activate, then speak your command.

---

## Setup

### 1. Install Dependencies:
```cmd
pip install -r requirements.txt
```

### 2. Configure Settings:
Edit `config.json` to customize all parameters:

```json
{
  "groq": {
    "primary_model": "whisper-large-v3",
    "fallback_model": "whisper-large-v3-turbo"
  },
  "ollama": {
    "model": "rnj-1:8b-cloud",
    "host": "http://localhost:11434"
  },
  "language": {
    "code": "fr"
  },
  "wake_word": {
    "word": "computer"
  },
  "audio": {
    "sample_rate": 16000,
    "tts_speed": "normal"
  }
}
```

### 3. Configure API Key:
Edit `var_venv` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Ensure Ollama is Running:
Make sure Ollama is installed and the `rnj-1:8b-cloud` model is available:
```cmd
ollama pull rnj-1:8b-cloud
ollama serve
```

---

## Features

### Multi-Language Support
- Supports 50+ languages for speech recognition and TTS
- Configure via `LANGUAGE` variable (default: French "fr")
- Works with: English, French, Spanish, German, Italian, Portuguese, Arabic, Japanese, Chinese, and more

### Speech-to-Text (STT)
- **Primary Model**: whisper-large-v3
- **Fallback Model**: whisper-large-v3-turbo (on rate limit)
- Automatic failover on `RateLimitError`

### LLM
- Local Ollama instance
- Model: `rnj-1:8b-cloud`

### Text-to-Speech (TTS)
- Google TTS (gTTS)
- Automatic playback on Windows

---

## Customization

All settings are now centralized in `config.json`:

### Language Settings:
```json
"language": {
  "code": "fr",
  "name": "French"
}
```
Supported codes: `en`, `fr`, `es`, `de`, `it`, `pt`, `ar`, `ja`, `zh`, `ru`, `nl`, `pl`, `tr`, `ko`, `hi`, etc.

### Wake Word (assistant.py):
```json
"wake_word": {
  "word": "computer",
  "alternatives": ["ordinateur", "assistant", "jarvis"]
}
```

### Ollama Model:
```json
"ollama": {
  "model": "rnj-1:8b-cloud",
  "host": "http://localhost:11434"
}
```

### Audio Settings:
```json
"audio": {
  "sample_rate": 16000,
  "silence_duration": 2.0,
  "wake_word_listen_duration": 3,
  "command_listen_duration": 5,
  "tts_speed": "normal"
}
```
Set `tts_speed` to `"slow"` for slower speech.

### Groq Models:
```json
"groq": {
  "primary_model": "whisper-large-v3",
  "fallback_model": "whisper-large-v3-turbo"
}
```

### Playback Timing:
```json
"playback": {
  "words_per_minute": 150,
  "buffer_seconds": 2
}
```

---

## Troubleshooting

### No audio detected:
- Check microphone permissions
- Ensure microphone is set as default input device

### Groq API errors:
- Verify `GROQ_API_KEY` in `var_venv`
- Check API rate limits

### Ollama connection failed:
- Ensure Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`

---

## Requirements
- Python 3.10+
- Working microphone
- Internet connection (for Groq STT and gTTS)
- Ollama running locally
