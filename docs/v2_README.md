# Voice Assistant V2 - Advanced Edition

A sophisticated voice assistant with conversation context, streaming responses, multiple TTS engines, and extensible architecture.

## 🚀 What's New in V2

### Core Improvements
- **Conversation Context**: Maintains conversation history across interactions
- **Streaming Responses**: Real-time LLM response generation
- **Voice Activity Detection (VAD)**: Better speech detection using WebRTC VAD
- **Multi-Engine TTS**: Support for gTTS, Edge TTS, and pyttsx3
- **Session Management**: Save and load conversation sessions
- **Performance Metrics**: Track latency and usage statistics
- **Modular Architecture**: Clean separation of concerns

### Advanced Features
- **Interruption Detection**: Stop speaking when user interrupts (configurable)
- **Smart Audio Recording**: Automatic silence detection with VAD
- **Conversation Commands**: Voice commands to control the assistant
- **Color-coded Console**: Better visual feedback (requires colorama)
- **Graceful Shutdown**: Proper cleanup and session saving

## 📁 Project Structure

```
v2/
├── assistant.py              # Main assistant application
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── core/                     # Core modules
│   ├── __init__.py
│   ├── config_manager.py    # Configuration management
│   ├── audio_manager.py     # Audio recording with VAD
│   ├── conversation_manager.py  # Context and history
│   └── tts_manager.py       # Multi-engine TTS
└── sessions/                 # Saved conversation sessions (auto-created)
```

## 🛠️ Installation

### 1. Install Dependencies

```cmd
cd v2
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `config.json` to customize:

```json
{
  "ollama": {
    "model": "rnj-1:8b-cloud",
    "stream": true,
    "temperature": 0.7
  },
  "language": {
    "code": "fr"
  },
  "wake_word": {
    "enabled": true,
    "word": "computer"
  },
  "tts": {
    "engine": "gtts",
    "speed": "normal"
  },
  "conversation": {
    "max_history": 10,
    "save_sessions": true
  }
}
```

### 3. Set API Key

Ensure `../var_venv` contains:
```
GROQ_API_KEY=your_api_key_here
```

### 4. Start Ollama

```cmd
ollama serve
```

## 🎯 Usage

### Start the Assistant

```cmd
python assistant.py
```

### Voice Commands

- **"computer"** (or your wake word) - Activate the assistant
- **"exit"** / **"goodbye"** - Shut down the assistant
- **"clear history"** - Reset conversation context
- **"save session"** - Manually save current session

### Example Interaction

```
💤 Listening for wake word: 'computer'...
   Heard: 'computer'
✅ Wake word detected!
🎤 Listening for your command...
📝 You: What's the weather like today?
🤖 Thinking (rnj-1:8b-cloud)...
💬 Assistant: I don't have access to real-time weather data...
🔊 Speaking...
```

## ⚙️ Configuration Guide

### Language Settings

```json
"language": {
  "code": "fr",
  "name": "French"
}
```

Supported: `en`, `fr`, `es`, `de`, `it`, `pt`, `ar`, `ja`, `zh`, `ru`, `nl`, `pl`, `tr`, `ko`, `hi`

### TTS Engines

**gTTS** (Google TTS - requires internet):
```json
"tts": {
  "engine": "gtts",
  "speed": "normal"
}
```

**Edge TTS** (Microsoft - requires internet, better quality):
```json
"tts": {
  "engine": "edge",
  "speed": "normal"
}
```

**pyttsx3** (Offline - no internet required):
```json
"tts": {
  "engine": "pyttsx3",
  "speed": "normal"
}
```

### Voice Activity Detection

Enable WebRTC VAD for better speech detection:

```json
"audio": {
  "vad_enabled": true,
  "vad_aggressiveness": 2,
  "silence_duration": 1.5
}
```

Aggressiveness levels: 0 (least aggressive) to 3 (most aggressive)

### Conversation Settings

```json
"conversation": {
  "max_history": 10,
  "save_sessions": true,
  "session_dir": "sessions",
  "system_prompt": "You are a helpful voice assistant..."
}
```

### Performance Monitoring

```json
"performance": {
  "log_metrics": true,
  "show_latency": true
}
```

Shows timing for STT, LLM, and TTS operations.

### Streaming Mode

```json
"ollama": {
  "stream": true
}
```

When enabled, LLM responses are displayed in real-time as they're generated.

## 📊 Session Management

### Automatic Saving

Sessions are automatically saved on shutdown to `sessions/` directory.

### Session Files

Each session is saved as JSON:
```json
{
  "session_id": "20260220_123456",
  "start_time": "2026-02-20T12:34:56",
  "history": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2026-02-20T12:35:00"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": "2026-02-20T12:35:02"
    }
  ]
}
```

### Export Sessions

Sessions can be exported to readable text format (feature in code, can be extended).

## 🎨 Console Colors

Install colorama for colored output:
```cmd
pip install colorama
```

Colors indicate:
- 🟢 Green: User input, success
- 🔵 Blue: Assistant responses
- 🟡 Yellow: Warnings, heard text
- 🔴 Red: Errors
- 🔵 Cyan: System messages

## 🔧 Advanced Features

### Interruption Detection

```json
"interruption": {
  "enabled": true,
  "detection_threshold": 0.02,
  "check_interval": 0.5
}
```

Allows stopping TTS when user starts speaking (experimental).

### Custom System Prompt

Customize the assistant's behavior:

```json
"conversation": {
  "system_prompt": "You are a French-speaking assistant specialized in cooking. Keep responses brief and practical."
}
```

### Ollama Parameters

```json
"ollama": {
  "model": "rnj-1:8b-cloud",
  "temperature": 0.7,
  "context_window": 4096,
  "stream": true
}
```

## 📈 Performance Metrics

On shutdown, see performance stats:

```
📊 Performance Metrics:
   Total interactions: 5
   Avg STT time: 1.23s
   Avg LLM time: 2.45s
   Avg TTS time: 3.12s
```

## 🐛 Troubleshooting

### VAD Not Working

If WebRTC VAD is not available:
```cmd
pip install webrtcvad
```

Or disable in config:
```json
"audio": {
  "vad_enabled": false
}
```

### Edge TTS Not Working

```cmd
pip install edge-tts
```

### pyttsx3 Not Working

```cmd
pip install pyttsx3
```

On Windows, pyttsx3 uses SAPI5 (built-in).

### Ollama Connection Failed

Ensure Ollama is running:
```cmd
ollama serve
```

Check the host in config:
```json
"ollama": {
  "host": "http://localhost:11434"
}
```

### No Audio Detected

- Check microphone permissions
- Adjust `silence_threshold` in config
- Try disabling VAD

## 🔮 Future Enhancements

Planned features for future versions:
- Plugin system for tools/functions
- Web UI interface
- Emotion detection in responses
- Multi-user support
- Cloud TTS options (ElevenLabs, etc.)
- Wake word training
- Noise cancellation

## 📝 Comparison: V1 vs V2

| Feature | V1 | V2 |
|---------|----|----|
| Conversation Context | ❌ | ✅ |
| Streaming Responses | ❌ | ✅ |
| VAD | ❌ | ✅ |
| Multiple TTS Engines | ❌ | ✅ |
| Session Management | ❌ | ✅ |
| Performance Metrics | ❌ | ✅ |
| Modular Architecture | ❌ | ✅ |
| Color Console | ❌ | ✅ |
| Voice Commands | ❌ | ✅ |

## 📄 License

MIT

## 🤝 Contributing

V2 is designed to be extensible. Key extension points:
- Add new TTS engines in `tts_manager.py`
- Add plugins in a new `plugins/` directory
- Extend conversation manager for advanced context handling
- Add new audio processing in `audio_manager.py`
