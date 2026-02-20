# Usage Guide

## Quick Start

### 1. Run V2 (Recommended)
```cmd
python v2/assistant.py
```

**What happens:**
- System initializes
- Listens for wake word "computer"
- You say "computer"
- System listens for your command
- Processes with LLM
- Speaks response
- Returns to listening for wake word

**Voice Commands:**
- "computer" - Activate
- "exit" or "goodbye" - Quit
- "clear history" - Reset conversation
- "save session" - Save manually

### 2. Run V1 (Simple)
```cmd
python v1/assistant.py
```

**What happens:**
- System initializes
- Listens for wake word "computer"
- You say "computer"
- System listens for your command
- Processes with LLM
- Speaks response
- Returns to listening for wake word

**To exit:** Press Ctrl+C

### 3. Run V1 Single-Shot
```cmd
python v1/main.py
```

**What happens:**
- Records your voice (auto-stops after silence)
- Transcribes
- Gets LLM response
- Speaks response
- Exits

## Configuration

### Change Language

Edit `v1/config.json` or `v2/config.json`:
```json
"language": {
  "code": "fr"
}
```

Options: `en`, `fr`, `es`, `de`, `it`, `pt`, `ar`, `ja`, `zh`, etc.

### Change Wake Word

```json
"wake_word": {
  "word": "assistant"
}
```

Try: `computer`, `assistant`, `jarvis`, `hey there`

### Change Ollama Model

```json
"ollama": {
  "model": "llama2"
}
```

Make sure to pull the model first:
```cmd
ollama pull llama2
```

### V2: Change TTS Engine

```json
"tts": {
  "engine": "edge"
}
```

Options:
- `gtts` - Google TTS (internet required)
- `edge` - Microsoft Edge TTS (internet, better quality)
- `pyttsx3` - Offline (no internet needed)

## Typical Workflow

### V2 Example Session

```
$ python v2/assistant.py

============================================================
🎙️  VOICE ASSISTANT V2 - READY
============================================================
Say 'computer' to activate

💤 Listening for wake word: 'computer'...
   Heard: 'computer'
✅ Wake word detected!

🎤 Listening for your command...
📝 You: What's the capital of France?

🤖 Thinking (rnj-1:8b-cloud)...
💬 Assistant: The capital of France is Paris.

🔊 Speaking...
✅ Response complete

💤 Listening for wake word: 'computer'...
   Heard: 'computer'
✅ Wake word detected!

🎤 Listening for your command...
📝 You: Tell me more about it

🤖 Thinking (rnj-1:8b-cloud)...
💬 Assistant: Paris is the largest city in France...
[Uses conversation context!]

🔊 Speaking...
✅ Response complete

💤 Listening for wake word: 'computer'...
   Heard: 'exit'
👋 Goodbye!

📊 Performance Metrics:
   Total interactions: 2
   Avg STT time: 1.23s
   Avg LLM time: 2.45s
   Avg TTS time: 3.12s

💾 Session saved: sessions/session_20260220_010719.json
```

## Tips

### For Best Results

1. **Speak clearly** - Normal pace, clear pronunciation
2. **Wait for confirmation** - Let system acknowledge wake word
3. **Quiet environment** - Minimize background noise
4. **Good microphone** - Use quality mic for better recognition

### V2 Specific

1. **Use context** - Ask follow-up questions
2. **Check sessions** - Review saved conversations in `v2/sessions/`
3. **Monitor metrics** - See performance stats on exit
4. **Try different TTS** - Edge TTS has better quality

### Troubleshooting

**No wake word detected:**
- Speak louder
- Say wake word clearly
- Check microphone is working
- Try different wake word

**Poor transcription:**
- Reduce background noise
- Speak more clearly
- Check internet connection (for Groq API)

**LLM not responding:**
- Verify Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Try different model in config

**No audio output:**
- Check speakers/headphones
- Verify TTS engine in config
- Try different TTS engine (V2)

## Advanced Usage

### V2: Load Previous Session

Currently manual - check `v2/sessions/` directory for saved JSON files.

### V2: Custom System Prompt

Edit `v2/config.json`:
```json
"conversation": {
  "system_prompt": "You are a helpful French tutor. Always respond in French."
}
```

### V2: Adjust VAD Sensitivity

```json
"audio": {
  "vad_enabled": true,
  "vad_aggressiveness": 2
}
```

Levels: 0 (least) to 3 (most aggressive)

### V2: Performance Tuning

```json
"ollama": {
  "stream": true,
  "temperature": 0.7
},
"performance": {
  "log_metrics": true,
  "show_latency": true
}
```

## Keyboard Shortcuts

- **Ctrl+C** - Stop/Exit (both versions)
- **V2 only:** Say "exit" or "goodbye" for graceful shutdown

## File Locations

### V1
- Config: `v1/config.json`
- Scripts: `v1/assistant.py`, `v1/main.py`

### V2
- Config: `v2/config.json`
- Scripts: `v2/assistant.py`
- Sessions: `v2/sessions/` (auto-created)
- Core modules: `v2/core/`

### Shared
- API Keys: `var_venv` (project root)

## Next Steps

1. Try both versions
2. Experiment with different languages
3. Test conversation context (V2)
4. Customize system prompt (V2)
5. Try different TTS engines (V2)
6. Review saved sessions (V2)

---

**Need Help?**
- Check `QUICKSTART.md` for setup
- Read `COMPARISON.md` for V1 vs V2
- See `FIXED_ISSUES.md` for troubleshooting
