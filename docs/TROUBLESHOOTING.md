# Voice Assistant V3 - Troubleshooting Guide

Common issues and solutions for the PyQt6 GUI version.

## 🔍 Quick Diagnostics

Run the test suite first:
```cmd
cd v3
python test_gui.py
```

This will identify most common issues.

## 🐛 Common Issues

### 1. Window Doesn't Open

#### Symptom
```
No error, but window doesn't appear
```

#### Causes & Solutions

**A. PyQt6 not installed**
```cmd
pip install PyQt6
```

**B. Display environment not available**
- Check if running on headless server
- Use V2 instead for headless environments
- Enable X11 forwarding if using SSH

**C. Python version too old**
```cmd
python --version  # Should be 3.8+
```

**D. Display scaling issues**
- Try different display scaling
- Check system display settings
- Run with: `python assistant_gui.py --no-scaling`

### 2. Import Errors

#### Symptom
```
ModuleNotFoundError: No module named 'PyQt6'
```

#### Solution
Install all dependencies:
```cmd
cd v3
pip install -r requirements.txt
```

#### Specific Modules

**PyQt6:**
```cmd
pip install PyQt6
```

**Groq:**
```cmd
pip install groq
```

**Ollama:**
```cmd
pip install ollama
```

**Audio packages:**
```cmd
pip install sounddevice numpy SpeechRecognition
```

**TTS packages:**
```cmd
pip install gTTS edge-tts pyttsx3
```

### 3. No Audio Detected

#### Symptom
```
Status: "No audio detected"
```

#### Causes & Solutions

**A. Microphone not connected**
- Check physical connection
- Verify microphone in system settings

**B. Permissions not granted**

Windows:
1. Settings → Privacy → Microphone
2. Allow apps to access microphone
3. Allow Python to access microphone

macOS:
1. System Preferences → Security & Privacy
2. Privacy → Microphone
3. Add Python/Terminal

Linux:
```cmd
# Check audio devices
arecord -l

# Test recording
arecord -d 3 test.wav
aplay test.wav
```

**C. Wrong audio device**

Check available devices:
```python
import sounddevice as sd
print(sd.query_devices())
```

**D. Test without voice**
Use manual input to test:
1. Click "⌨️ Type Message"
2. Enter text
3. Verify LLM and TTS work

### 4. Groq API Errors

#### Symptom
```
Error: Groq API error: 401 Unauthorized
```

#### Causes & Solutions

**A. API key not set**

Check `var_venv` file exists in project root:
```
GROQ_API_KEY=your_key_here
```

**B. Invalid API key**
- Verify key at https://console.groq.com
- Generate new key if needed
- Update `var_venv` file

**C. Rate limit exceeded**
```
Error: RateLimitError
```

Solution:
- Wait a few minutes
- Uses fallback model automatically
- Check Groq dashboard for limits

**D. No internet connection**
- Verify internet access
- Check firewall settings
- Try: `ping api.groq.com`

### 5. Ollama Connection Failed

#### Symptom
```
Error: Connection refused to localhost:11434
```

#### Causes & Solutions

**A. Ollama not running**
```cmd
# Start Ollama
ollama serve
```

**B. Model not installed**
```cmd
# List models
ollama list

# Install model
ollama pull rnj-1:8b-cloud
```

**C. Wrong host/port**

Check config.json:
```json
{
  "ollama": {
    "host": "http://localhost:11434"
  }
}
```

**D. Firewall blocking**
- Allow Ollama through firewall
- Check port 11434 is open

### 6. TTS Not Working

#### Symptom
```
No audio output after response
```

#### Causes & Solutions

**A. TTS engine not installed**

gTTS:
```cmd
pip install gTTS
```

Edge TTS:
```cmd
pip install edge-tts
```

pyttsx3:
```cmd
pip install pyttsx3
```

**B. No internet (gTTS/Edge)**
- gTTS and Edge TTS require internet
- Use pyttsx3 for offline TTS
- Change in Settings panel

**C. Audio output device**
- Check system audio settings
- Verify speakers/headphones
- Test with system sounds

**D. File permissions**
- TTS creates temp files
- Check write permissions
- Check disk space

### 7. Wake Word Not Detected

#### Symptom
```
Says "Heard: ..." but never detects wake word
```

#### Causes & Solutions

**A. Wrong wake word**

Check config.json:
```json
{
  "wake_word": {
    "word": "computer"
  }
}
```

Say exactly: "computer"

**B. Pronunciation**
- Speak clearly
- Try alternatives in config
- Adjust sensitivity

**C. Background noise**
- Reduce background noise
- Move closer to microphone
- Increase microphone volume

**D. Language mismatch**
- Wake word detection uses Google Speech
- Check language setting matches
- Try English wake word first

### 8. GUI Freezes

#### Symptom
```
Window becomes unresponsive
```

#### Causes & Solutions

**A. Long-running operation**
- Should not happen (uses threads)
- Check console for errors
- Restart application

**B. Deadlock**
- Rare threading issue
- Restart application
- Report bug with console output

**C. Resource exhaustion**
- Check RAM usage
- Close other applications
- Restart computer

### 9. Config File Errors

#### Symptom
```
Error: Config file not found
Error: Missing required config section
```

#### Solutions

**A. File missing**
```cmd
# Copy from example
cp config.json.example config.json
```

**B. Invalid JSON**
- Check for syntax errors
- Use JSON validator
- Compare with example

**C. Missing sections**

Required sections:
- groq
- ollama
- language
- audio
- tts
- conversation
- ui

### 10. Session Save Fails

#### Symptom
```
Error saving session
```

#### Causes & Solutions

**A. Directory doesn't exist**
```cmd
mkdir sessions
```

**B. No write permissions**
```cmd
# Windows
icacls sessions /grant Users:F

# Linux/macOS
chmod 755 sessions
```

**C. Disk full**
- Check disk space
- Clean old sessions

## 🔧 Advanced Troubleshooting

### Enable Debug Mode

Add to assistant_gui.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Dependencies

```cmd
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import groq; print('Groq OK')"
python -c "import ollama; print('Ollama OK')"
python -c "import sounddevice; print('Audio OK')"
```

### Test Components Individually

```cmd
# Test config
python -c "from core.config_manager import ConfigManager; c = ConfigManager('config.json'); print('Config OK')"

# Test audio
python -c "from core.audio_manager import AudioManager; from core.config_manager import ConfigManager; c = ConfigManager('config.json'); a = AudioManager(c); print('Audio OK')"

# Test TTS
python -c "from core.tts_manager import TTSManager; from core.config_manager import ConfigManager; c = ConfigManager('config.json'); t = TTSManager(c); print('TTS OK')"
```

### Check System Resources

```cmd
# Windows
tasklist | findstr python

# Linux/macOS
ps aux | grep python
top -p $(pgrep python)
```

## 📊 Error Messages Reference

### "Unable to import PyQt6"
→ Install: `pip install PyQt6`

### "Config file not found"
→ Run from v3 directory: `cd v3`

### "No module named 'core'"
→ Run from v3 directory: `cd v3`

### "API key not found"
→ Create `var_venv` file with `GROQ_API_KEY=...`

### "Connection refused"
→ Start Ollama: `ollama serve`

### "No audio detected"
→ Check microphone permissions

### "Rate limit exceeded"
→ Wait a few minutes, uses fallback automatically

### "Model not found"
→ Install model: `ollama pull rnj-1:8b-cloud`

## 🆘 Getting Help

### 1. Check Console Output
Look for detailed error messages in the terminal

### 2. Run Test Suite
```cmd
python test_gui.py
```

### 3. Check Logs
Look for error messages in console output

### 4. Verify Setup
```cmd
# Check Python version
python --version

# Check pip packages
pip list | grep -E "PyQt6|groq|ollama"

# Check Ollama
ollama list
```

### 5. Try V2
If V3 doesn't work, try V2:
```cmd
cd ../v2
python assistant.py
```

## 🔄 Reset to Defaults

### Clean Install

```cmd
# Remove virtual environment
rm -rf venv

# Create new environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Reset Config

```cmd
# Backup current config
cp config.json config.json.backup

# Copy default config
cp config.json.example config.json
```

### Clear Sessions

```cmd
# Backup sessions
cp -r sessions sessions_backup

# Clear sessions
rm -rf sessions/*
```

## 🐛 Known Issues

### Issue 1: Window Position
**Problem**: Window opens off-screen  
**Workaround**: Delete Qt settings file

### Issue 2: High DPI Scaling
**Problem**: Blurry text on high DPI displays  
**Workaround**: Adjust display scaling in system settings

### Issue 3: Audio Latency
**Problem**: Delay between speech and response  
**Workaround**: Use pyttsx3 for faster TTS

## 📝 Reporting Bugs

When reporting issues, include:

1. **Error message** (full text)
2. **Console output** (copy all)
3. **System info**:
   - OS and version
   - Python version
   - PyQt6 version
4. **Steps to reproduce**
5. **Test suite results**

## ✅ Verification Checklist

Before reporting a bug, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Running from v3 directory
- [ ] Config file exists and valid
- [ ] API key set in var_venv
- [ ] Ollama running
- [ ] Model installed
- [ ] Microphone connected
- [ ] Microphone permissions granted
- [ ] Internet connection working
- [ ] Test suite passes

## 🎯 Quick Fixes

### Can't hear responses
→ Change TTS engine in Settings panel

### Wake word not working
→ Use manual input (Ctrl+T) instead

### GUI won't start
→ Use V2 (terminal version)

### Slow responses
→ Check internet connection and Ollama

### High memory usage
→ Clear conversation history (Ctrl+D)

---

**Still having issues?** Try the test suite: `python test_gui.py`
