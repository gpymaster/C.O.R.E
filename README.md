# C.O.R.E — Cognitive Operations & Response Engine

A JARVIS-inspired autonomous AI voice assistant for macOS. C.O.R.E listens for a wake word, understands natural language, routes requests to the right system, and responds with a British TTS voice — all in real time.

---

## What It Does

- **Wake word detection** — say "Jarvis" to activate; enters conversation mode automatically
- **Intent routing** — uses a local Ollama LLM to classify requests into actions (ask AI, search Google, play a song, get weather, get time)
- **AI conversation** — multi-turn dialogue powered by a local Llama model with conversation history
- **Google Calendar integration** — reads and manages calendar events
- **Canvas LMS integration** — fetches course data and summaries
- **Weather forecasts** — pulls live weather via API
- **Text-to-speech** — responds in a British male voice using Edge TTS
- **Outward notifications** — proactive alerts when CORE has something to tell you

---

## Tech Stack

| Layer | Technology |
|---|---|
| Speech-to-text | AssemblyAI Streaming + SpeechRecognition (Google) |
| Local LLM | Ollama (Llama) |
| Cloud AI | Google Gemini |
| Text-to-speech | Edge TTS (`en-GB-RyanNeural`) |
| Audio playback | Pygame |
| Calendar | Google Calendar API |
| LMS | Canvas API |
| Weather | OpenWeatherMap / weather API |
| Vision | Llama Vision (local) |

---

## Project Structure

```
C.O.R.E.py              # Main entry point — wake word loop, intent pipeline
intent_ai.py            # Intent classification via Ollama
llama_text_ai.py        # Conversational AI with history
llama_text_no_history.py # Single-turn AI responses
Converstion_action.py   # Conversation action handler
Outward_action_ai.py    # Proactive notification system
Weather_api.py          # Weather data fetching
Canvas_api.py           # Canvas LMS integration
Google_calendar.py      # Google Calendar integration
History.json            # Conversation history store
Actions.json            # Registered action definitions
```

---

## Setup

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) running locally with a Llama model pulled
- A microphone

### Install dependencies

```bash
pip install assemblyai speechrecognition pygame edge-tts google-generativeai pywhatkit
```

### API Keys

Create a `.env` or set these directly in the relevant files:

- `ASSEMBLYAI_API_KEY` — for streaming speech recognition
- Google Calendar OAuth credentials → `google_calender_passkey.json` + `token.pickle`
- Canvas API token (in `Canvas_api.py`)
- OpenWeatherMap API key (in `Weather_api.py`)

### Run

```bash
python C.O.R.E.py
```

Say **"Jarvis"** to wake it up.

---

## Roadmap

C.O.R.E is being built toward full JARVIS-level autonomy. See [JARVIS_BLUEPRINT.md](JARVIS_BLUEPRINT.md) for the complete design spec.

**Planned phases:**
1. Advanced chain-of-thought reasoning (Claude / Gemini)
2. 50+ action system with safety validation
3. Background monitoring threads (calendar, email, system health, context)
4. Multi-modal vision & document analysis
5. macOS deep integration via AppleScript
6. Pattern learning & proactive suggestions

---

## License

MIT
