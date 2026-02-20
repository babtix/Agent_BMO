# Voice Assistant V3 - PyQt6 GUI Edition

A modern desktop application with a beautiful graphical interface for voice interaction.

## 🎨 What's New in V3

### Visual Interface
- **Modern GUI** - Clean, dark-themed interface
- **Real-time Feedback** - Visual status updates
- **Conversation Display** - Color-coded message history
- **Control Panel** - Easy-to-use buttons
- **Settings Panel** - Change language and TTS on the fly

### Features
- ✅ All V2 features (context, streaming, VAD, etc.)
- ✅ Beautiful PyQt6 interface
- ✅ Visual conversation history
- ✅ Manual text input option
- ✅ Real-time status updates
- ✅ Settings without editing config
- ✅ Menu bar with save/export
- ✅ Dark theme
- ✅ Responsive design

## 📸 Interface

```
┌─────────────────────────────────────────────┐
│  🎙️ Voice Assistant V3                      │
├─────────────────────────────────────────────┤
│                                             │
│  [Conversation Display Area]                │
│  - Color-coded messages                     │
│  - Timestamps                               │
│  - Scrollable history                       │
│                                             │
├─────────────────────────────────────────────┤
│  Controls:                                  │
│  [🎤 Start]  [⌨️ Type]  [🗑️ Clear]         │
├─────────────────────────────────────────────┤
│  Settings:                                  │
│  Language: [English ▼]                      │
│  TTS Engine: [gTTS ▼]                       │
├─────────────────────────────────────────────┤
│  Status: Ready                              │
└─────────────────────────────────────────────┘
```

## 🚀 Installation

### 1. Install Dependencies

```cmd
cd v3
pip install -r requirements.txt
```

### 2. Run the Application

```cmd
python assistant_gui.py
```

## 🎯 Usage

### Starting the Assistant

1. **Launch**: Run `python assistant_gui.py`
2. **Click "Start Listening"**: Begins listening for wake word
3. **Say wake word**: Default is "computer"
4. **Speak your command**: After wake word is detected
5. **Get response**: See and hear the response

### Manual Input

- Click **"Type Message"** button
- Enter text in the dialog
- Get response without voice input

### Changing Settings

**Language:**
- Select from dropdown in Settings panel
- Changes apply immediately

**TTS Engine:**
- Choose between gTTS, Edge TTS, or pyttsx3
- Changes apply to next response

### Menu Options

**File Menu:**
- **Save Session** - Save current conversation
- **Export Session** - Export to text file
- **Exit** - Close application

**Help Menu:**
- **About** - Show version and features

## 🎨 Interface Elements

### Conversation Display
- **Green** - Your messages
- **Blue** - Assistant responses
- **Orange** - System messages
- **Red** - Errors
- **Gray** - Status updates

### Control Buttons

**🎤 Start/Stop Listening**
- Toggle wake word detection
- Green when active

**⌨️ Type Message**
- Manual text input
- Useful for testing

**🗑️ Clear History**
- Reset conversation
- Clears display and context

### Status Bar
- Shows current activity
- Real-time updates
- Error messages

## ⚙️ Configuration

Edit `v3/config.json` for advanced settings:

```json
{
  "ui": {
    "theme": "dark",
    "window_width": 800,
    "window_height": 600,
    "font_size": 12
  },
  "wake_word": {
    "word": "computer"
  },
  "language": {
    "code": "en"
  }
}
```

## 🎨 Themes

### Dark Theme (Default)
- Dark background
- High contrast
- Easy on eyes
- Professional look

### Customization
Edit stylesheet in `assistant_gui.py` to customize colors.

## 🔧 Advanced Features

### Background Processing
- Voice processing runs in separate thread
- UI remains responsive
- No freezing during recognition

### Session Management
- Auto-save on exit
- Manual save option
- Export to text format

### Error Handling
- Visual error messages
- Graceful degradation
- Detailed status updates

## 📊 Comparison: V2 vs V3

| Feature | V2 (Console) | V3 (GUI) |
|---------|--------------|----------|
| Interface | Terminal | Desktop App |
| Visual Feedback | Text only | Color-coded |
| Settings | Edit config | UI controls |
| History View | Scrolling text | Rich display |
| Manual Input | No | Yes |
| Status Updates | Print | Status bar |
| Session Export | JSON only | JSON + TXT |
| User Experience | Developer | End-user |

## 🎯 Use Cases

### V3 is Perfect For:
- ✅ End users (non-technical)
- ✅ Desktop application
- ✅ Visual feedback needed
- ✅ Easy settings changes
- ✅ Professional presentation
- ✅ Demo/showcase
- ✅ Daily use

## 🐛 Troubleshooting

### Window doesn't open
```cmd
pip install PyQt6
```

### No audio detected
- Check microphone in system settings
- Grant microphone permissions
- Test with "Type Message" first

### UI looks wrong
- Check PyQt6 installation
- Try restarting application
- Check display scaling settings

## 🔮 Future Enhancements

Planned for V3.1:
- [ ] Waveform visualization
- [ ] Voice activity indicator
- [ ] Multiple themes (light/dark)
- [ ] Customizable hotkeys
- [ ] System tray integration
- [ ] Notification support
- [ ] Settings dialog
- [ ] Session browser

## 📝 Keyboard Shortcuts

- **Ctrl+L** - Toggle listening (Start/Stop)
- **Ctrl+T** - Type message (manual input)
- **Ctrl+D** - Clear conversation history
- **Ctrl+S** - Save session
- **Ctrl+E** - Export session
- **Ctrl+Q** - Quit application

## 🎓 Tips

### For Best Experience:
1. Use on a desktop/laptop (not headless server)
2. Ensure good microphone quality
3. Minimize background noise
4. Keep window visible for status updates
5. Use manual input for testing

### Performance:
- GUI adds minimal overhead
- Background threads keep UI responsive
- Same core performance as V2

## 📦 Dependencies

- PyQt6 - GUI framework
- All V2 dependencies
- Platform: Windows, macOS, Linux

## 🤝 Contributing

V3 is designed to be extended:
- Add new themes
- Create custom widgets
- Implement visualizations
- Add keyboard shortcuts

## 📄 License

MIT License - Same as V1 and V2

---

**Version**: 3.0.0  
**Status**: Production Ready ✅  
**Platform**: Cross-platform (Windows, macOS, Linux)
