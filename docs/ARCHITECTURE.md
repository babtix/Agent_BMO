# Voice Assistant V3 - Architecture

Technical architecture and design documentation.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Assistant V3                        │
│                     (PyQt6 GUI App)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Main Components                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GUI Layer  │  │ Worker Thread│  │  Core Modules│     │
│  │   (PyQt6)    │◄─┤  (Voice)     │◄─┤  (Business)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Widgets    │  │   Signals    │  │   Managers   │     │
│  │   Controls   │  │   Slots      │  │   Services   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Groq    │  │  Ollama  │  │   TTS    │  │  Audio   │   │
│  │ Whisper  │  │   LLM    │  │ Engines  │  │  System  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Component Breakdown

### 1. GUI Layer (PyQt6)

```
VoiceAssistantGUI (QMainWindow)
├── Conversation Display (QTextEdit)
│   ├── Color-coded messages
│   ├── Timestamps
│   └── Auto-scroll
│
├── Control Panel (QGroupBox)
│   ├── Start/Stop Button
│   ├── Manual Input Button
│   └── Clear History Button
│
├── Settings Panel (QGroupBox)
│   ├── Language Selector (QComboBox)
│   └── TTS Engine Selector (QComboBox)
│
├── Menu Bar (QMenuBar)
│   ├── File Menu
│   │   ├── Save Session
│   │   ├── Export Session
│   │   └── Exit
│   └── Help Menu
│       └── About
│
└── Status Bar (QStatusBar)
    └── Real-time status updates
```

### 2. Worker Thread

```
VoiceWorker (QThread)
├── Modes
│   ├── wake_word - Listen for wake word
│   └── listen - Record command
│
├── Signals (Thread-safe)
│   ├── status_update(message, color)
│   ├── transcription_done(text)
│   ├── response_done(text)
│   └── error_occurred(error)
│
└── Processing
    ├── Audio recording
    ├── VAD detection
    └── Transcription
```

### 3. Core Modules

```
Core Modules
├── ConfigManager
│   ├── Load/save config
│   ├── Dot notation access
│   └── Validation
│
├── AudioManager
│   ├── Recording (simple/VAD)
│   ├── Device management
│   └── Cleanup
│
├── ConversationManager
│   ├── History tracking
│   ├── Context management
│   └── Session save/load
│
└── TTSManager
    ├── Multiple engines
    ├── Language support
    └── Voice control
```

## 🔄 Data Flow

### Voice Input Flow

```
1. User clicks "Start Listening"
   │
   ▼
2. GUI creates VoiceWorker (wake_word mode)
   │
   ▼
3. Worker records audio (3s)
   │
   ▼
4. Worker transcribes with Google Speech
   │
   ▼
5. Worker checks for wake word
   │
   ├─ Not found ─► Loop back to step 3
   │
   └─ Found ─► Emit transcription_done signal
              │
              ▼
6. GUI receives signal, creates new Worker (listen mode)
   │
   ▼
7. Worker records with VAD (10s max)
   │
   ▼
8. Worker transcribes with Groq Whisper
   │
   ▼
9. Worker emits transcription_done signal
   │
   ▼
10. GUI processes with LLM
    │
    ▼
11. GUI displays response
    │
    ▼
12. GUI speaks response (TTS)
    │
    ▼
13. Loop back to step 2 (if still listening)
```

### Manual Input Flow

```
1. User clicks "Type Message" or presses Ctrl+T
   │
   ▼
2. GUI shows input dialog
   │
   ▼
3. User enters text
   │
   ▼
4. GUI processes with LLM (same as step 10 above)
   │
   ▼
5. GUI displays response
   │
   ▼
6. GUI speaks response (TTS)
```

## 🧵 Threading Model

### Main Thread (GUI)
- **Responsibilities:**
  - UI rendering
  - Event handling
  - User interaction
  - Display updates

- **Does NOT:**
  - Block on I/O
  - Long computations
  - Network calls
  - Audio processing

### Worker Thread (Voice)
- **Responsibilities:**
  - Audio recording
  - Speech recognition
  - Transcription
  - VAD processing

- **Communication:**
  - Signals to main thread
  - Thread-safe only
  - No direct UI access

### Why Threading?
- ✅ Responsive UI
- ✅ No freezing
- ✅ Parallel processing
- ✅ Better UX

## 🎨 UI Component Hierarchy

```
QMainWindow (VoiceAssistantGUI)
│
├── Central Widget (QWidget)
│   └── Main Layout (QVBoxLayout)
│       │
│       ├── Title (QLabel)
│       │
│       ├── Conversation Display (QTextEdit)
│       │   └── Read-only, rich text
│       │
│       ├── Control Group (QGroupBox)
│       │   └── Control Layout (QHBoxLayout)
│       │       ├── Start Button (QPushButton)
│       │       ├── Manual Button (QPushButton)
│       │       └── Clear Button (QPushButton)
│       │
│       └── Settings Group (QGroupBox)
│           └── Settings Layout (QVBoxLayout)
│               ├── Language Layout (QHBoxLayout)
│               │   ├── Label (QLabel)
│               │   └── Combo (QComboBox)
│               │
│               └── TTS Layout (QHBoxLayout)
│                   ├── Label (QLabel)
│                   └── Combo (QComboBox)
│
├── Menu Bar (QMenuBar)
│   ├── File Menu (QMenu)
│   └── Help Menu (QMenu)
│
└── Status Bar (QStatusBar)
```

## 🔌 External Integrations

### Groq Whisper API
```
Purpose: Speech-to-text transcription
Flow:
  Audio File → Groq API → Transcription Text
Features:
  - High accuracy
  - Multi-language
  - Fallback model
  - Rate limit handling
```

### Ollama LLM
```
Purpose: Natural language understanding & generation
Flow:
  User Input → Ollama → Assistant Response
Features:
  - Local processing
  - Context awareness
  - Streaming support
  - Configurable model
```

### TTS Engines
```
gTTS (Google):
  - Cloud-based
  - High quality
  - Multi-language
  - Requires internet

Edge TTS (Microsoft):
  - Cloud-based
  - Natural voices
  - Multi-language
  - Requires internet

pyttsx3 (Offline):
  - Local processing
  - No internet needed
  - System voices
  - Instant response
```

### Audio System
```
sounddevice:
  - Audio recording
  - Device management
  - Real-time processing

SpeechRecognition:
  - Google Speech API
  - Wake word detection
  - Fallback recognition

webrtcvad:
  - Voice Activity Detection
  - Silence detection
  - Smart recording
```

## 📊 State Management

### Application States

```
States:
├── Idle
│   └── Ready for input
│
├── Listening (Wake Word)
│   ├── Recording audio
│   ├── Transcribing
│   └── Checking for wake word
│
├── Listening (Command)
│   ├── Recording with VAD
│   ├── Transcribing
│   └── Processing
│
├── Processing
│   ├── Querying LLM
│   └── Generating response
│
└── Speaking
    ├── Playing TTS
    └── Waiting for completion
```

### State Transitions

```
Idle ──[Start]──► Listening (Wake Word)
                        │
                        │ [Wake word detected]
                        ▼
                  Listening (Command)
                        │
                        │ [Audio recorded]
                        ▼
                    Processing
                        │
                        │ [Response ready]
                        ▼
                     Speaking
                        │
                        │ [Complete]
                        ▼
                  Listening (Wake Word)
                        │
                        │ [Stop]
                        ▼
                      Idle
```

## 🔐 Security Architecture

### API Key Management
```
Environment Variables (var_venv)
├── Not in code
├── Not in config
├── Not in version control
└── User-specific
```

### Data Privacy
```
Local Storage:
├── Sessions (local files)
├── Audio (temporary, deleted)
├── Config (local file)
└── No cloud sync
```

### Network Security
```
HTTPS Only:
├── Groq API (HTTPS)
├── TTS APIs (HTTPS)
└── No insecure connections
```

## 📁 File Structure

```
v3/
├── assistant_gui.py          # Main application (600+ lines)
│   ├── VoiceWorker class
│   ├── VoiceAssistantGUI class
│   └── main() function
│
├── core/                     # Core modules
│   ├── __init__.py
│   ├── audio_manager.py      # Audio recording & VAD
│   ├── config_manager.py     # Configuration
│   ├── conversation_manager.py  # Context & history
│   └── tts_manager.py        # Text-to-speech
│
├── config.json               # Configuration file
├── requirements.txt          # Dependencies
├── test_gui.py              # Test suite
├── example_usage.py         # Usage examples
│
└── sessions/                # Session storage
    └── session_*.json       # Saved sessions
```

## 🎯 Design Patterns

### Patterns Used

1. **MVC (Model-View-Controller)**
   - Model: Core modules
   - View: PyQt6 GUI
   - Controller: VoiceAssistantGUI

2. **Observer Pattern**
   - Signals and slots
   - Event-driven
   - Loose coupling

3. **Strategy Pattern**
   - Multiple TTS engines
   - Configurable behavior
   - Runtime selection

4. **Singleton Pattern**
   - ConfigManager
   - Single instance
   - Global access

5. **Factory Pattern**
   - Worker creation
   - Component initialization
   - Flexible instantiation

## 🔧 Configuration Architecture

```
config.json
├── groq
│   ├── api_key_env
│   ├── primary_model
│   └── fallback_model
│
├── ollama
│   ├── model
│   ├── host
│   └── parameters
│
├── language
│   ├── code
│   └── supported
│
├── wake_word
│   ├── word
│   └── alternatives
│
├── audio
│   ├── sample_rate
│   ├── vad_enabled
│   └── durations
│
├── tts
│   ├── engine
│   └── options
│
├── conversation
│   ├── max_history
│   └── system_prompt
│
└── ui
    ├── theme
    └── dimensions
```

## 🚀 Performance Considerations

### Optimization Strategies

1. **Threading**
   - Non-blocking UI
   - Parallel processing
   - Responsive interface

2. **Caching**
   - Config caching
   - Resource caching
   - Minimal reloads

3. **Lazy Loading**
   - On-demand imports
   - Deferred initialization
   - Fast startup

4. **Resource Management**
   - Automatic cleanup
   - Memory management
   - File cleanup

## 📈 Scalability

### Current Limits
- Conversation history: 10 messages (configurable)
- Audio recording: 30s max
- Session size: Unlimited
- Concurrent users: 1 (desktop app)

### Future Scalability
- Multi-user support
- Cloud sync
- Distributed processing
- Load balancing

## 🎓 Architecture Benefits

### Modularity
- ✅ Separated concerns
- ✅ Reusable components
- ✅ Easy to test
- ✅ Easy to extend

### Maintainability
- ✅ Clear structure
- ✅ Well-documented
- ✅ Consistent patterns
- ✅ Easy to debug

### Extensibility
- ✅ Plugin-ready
- ✅ Configurable
- ✅ Flexible design
- ✅ Future-proof

---

**Architecture Version**: 3.0.0  
**Last Updated**: 2026-02-20  
**Status**: Production Ready ✅
