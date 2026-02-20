# Voice Assistant V3 - Quick Start Guide

Get up and running with the PyQt6 GUI version in minutes!

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies

```cmd
cd v3
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `var_venv` file in the project root with your API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Run the Application

```cmd
python assistant_gui.py
```

That's it! The GUI should open.

## 🧪 Test First (Recommended)

Before running the full application, test your setup:

```cmd
python test_gui.py
```

This will check:
- ✅ All required packages installed
- ✅ Configuration file valid
- ✅ Core modules working
- ✅ GUI framework ready

## 🎯 First Use

1. **Launch**: Window opens with dark theme
2. **Click "Start Listening"**: Button turns red
3. **Say wake word**: Default is "computer"
4. **Speak command**: After wake word detected
5. **Get response**: See text and hear audio

## ⌨️ Keyboard Shortcuts

- **Ctrl+L** - Toggle listening
- **Ctrl+T** - Type message (manual input)
- **Ctrl+D** - Clear conversation history
- **Ctrl+S** - Save session
- **Ctrl+E** - Export session
- **Ctrl+Q** - Quit application

## 🎨 Interface Overview

```
┌─────────────────────────────────────┐
│  🎙️ Voice Assistant V3              │  ← Title
├─────────────────────────────────────┤
│                                     │
│  [Conversation Display]             │  ← Messages
│  - Color-coded                      │
│  - Timestamps                       │
│  - Scrollable                       │
│                                     │
├─────────────────────────────────────┤
│  [🎤 Start] [⌨️ Type] [🗑️ Clear]   │  ← Controls
├─────────────────────────────────────┤
│  Language: [English ▼]              │  ← Settings
│  TTS: [gTTS ▼]                      │
├─────────────────────────────────────┤
│  Status: Ready                      │  ← Status Bar
└─────────────────────────────────────┘
```

## 🎨 Color Coding

- **Green** - Your messages
- **Blue** - Assistant responses & system info
- **Orange** - Warnings & status changes
- **Red** - Errors
- **Gray** - Background activity

## ⚙️ Quick Settings

### Change Language

1. Click language dropdown
2. Select from 9 languages
3. Changes apply immediately

### Change TTS Engine

1. Click TTS dropdown
2. Choose: gTTS, Edge TTS, or pyttsx3
3. Next response uses new engine

### Change Wake Word

Edit `config.json`:

```json
{
  "wake_word": {
    "word": "jarvis"
  }
}
```

## 🔧 Common Issues

### "No module named PyQt6"

```cmd
pip install PyQt6
```

### "No audio detected"

1. Check microphone permissions
2. Test with "Type Message" button first
3. Check system audio settings

### "Groq API error"

1. Verify API key in `var_venv`
2. Check internet connection
3. Verify Groq account has credits

### Window doesn't open

1. Check Python version (3.8+)
2. Reinstall PyQt6: `pip install --upgrade PyQt6`
3. Try running test: `python test_gui.py`

## 🎯 Testing Without Voice

Use the **"Type Message"** button to test without microphone:

1. Click "⌨️ Type Message"
2. Enter text in dialog
3. Get response without voice

Perfect for:
- Testing setup
- Debugging
- Quiet environments
- No microphone available

## 📊 Features Checklist

After first run, you should have:

- ✅ GUI window opens
- ✅ Dark theme applied
- ✅ Can type messages
- ✅ Get LLM responses
- ✅ Hear TTS output
- ✅ Save/export sessions
- ✅ Change settings in UI

## 🔄 Workflow Example

### Typical Session:

1. **Start**: `python assistant_gui.py`
2. **Click**: "🎤 Start Listening"
3. **Say**: "computer" (wake word)
4. **Ask**: "What's the weather like?"
5. **Listen**: Response plays automatically
6. **Continue**: Keeps listening for wake word
7. **Stop**: Click "🛑 Stop Listening"
8. **Save**: Ctrl+S or File → Save Session

## 🎓 Pro Tips

### Tip 1: Manual Input for Testing
Use Ctrl+T to quickly test responses without voice

### Tip 2: Clear History
Use Ctrl+D to start fresh conversation context

### Tip 3: Session Management
Sessions auto-save on exit, find them in `sessions/` folder

### Tip 4: Multiple Languages
Switch language mid-conversation for multilingual support

### Tip 5: TTS Comparison
Try different TTS engines to find your favorite:
- **gTTS**: Best quality, requires internet
- **Edge TTS**: Microsoft voices, requires internet
- **pyttsx3**: Offline, instant, robotic

## 📁 File Structure

```
v3/
├── assistant_gui.py      ← Main application
├── config.json           ← Configuration
├── requirements.txt      ← Dependencies
├── test_gui.py          ← Test suite
├── QUICKSTART.md        ← This file
├── README.md            ← Full documentation
└── core/
    ├── audio_manager.py
    ├── config_manager.py
    ├── conversation_manager.py
    └── tts_manager.py
```

## 🆘 Getting Help

### Check Logs
Look at console output for detailed error messages

### Test Components
```cmd
python test_gui.py
```

### Verify Config
```cmd
python -c "from core.config_manager import ConfigManager; c = ConfigManager('config.json'); print('OK')"
```

### Check Ollama
```cmd
ollama list
ollama run rnj-1:8b-cloud "test"
```

## 🎉 Next Steps

Once running successfully:

1. **Customize**: Edit `config.json` for your preferences
2. **Explore**: Try different languages and TTS engines
3. **Integrate**: Use as daily assistant
4. **Extend**: Add custom features to the GUI

## 📚 More Information

- **Full Documentation**: See `README.md`
- **Configuration**: See `config.json` comments
- **Comparison**: See `COMPARISON_V1_V2_V3.md`

---

**Ready to go?** Run `python assistant_gui.py` and start talking! 🎙️
