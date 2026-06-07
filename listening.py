import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
import logging
from typing import Type
import requests
import json
import os

# API Keys
api_key = "-----API KEY----"


_context = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_ai(prompt, model="qwen2.5:0.5b"):
    """Fast AI using qwen2.5:0.5b"""
    global _context
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 100
        }
    }
    
    if _context is not None:
        payload["context"] = _context
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if 'context' in result:
            _context = result['context']
        
        return result.get('response', '').strip()
    except Exception as e:
        print(f"⚠️  AI Error: {e}")
        return ""

def detect_jarvis_command(text):
    """Detect if user is talking to Jarvis and extract the command"""
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Check if "jarvis" is mentioned
    if "jarvis" not in text_lower:
        return None
    
    # Send to AI to extract the command
    print("🤖 Processing with AI...")
    
    extract_prompt = f"""The user said: "{text}"

Extract what the user wants Jarvis to do. Return only the action/request, nothing else.

Request:"""
    
    request = ask_ai(extract_prompt)
    
    if request:
        return request
    
    return None

def classify_action(command):
    """Use AI to classify the command type"""
    
    actions = {
        "search_google": "Search Google",
        "search_youtube": "Search YouTube",
        "open_website": "Open website",
        "play_music": "Play music",
        "check_weather": "Check weather",
        "set_reminder": "Set reminder",
        "answer_question": "Answer question",
        "tell_joke": "Tell a joke"
    }
    
    prompt = f"""Match this request to ONE action. Return ONLY the action key (like "search_google").

Available actions:
{json.dumps(actions, indent=2)}

User request: "{command}"

Action:"""
    
    action = ask_ai(prompt).strip().lower()
    
    # Find matching action
    for key in actions.keys():
        if key in action:
            return key
    
    return "answer_question"

def extract_parameters(command, action_type):
    """Use AI to extract parameters from the command"""
    
    if action_type in ["search_google", "search_youtube"]:
        prompt = f"""Extract the search query from this request. Return only the query.

Request: "{command}"

Query:"""
        return {"query": ask_ai(prompt)}
    
    elif action_type == "play_music":
        prompt = f"""Extract the song or artist name. Return only the name.

Request: "{command}"

Name:"""
        return {"song": ask_ai(prompt)}
    
    elif action_type == "check_weather":
        prompt = f"""Extract the location. If no location mentioned, return "current location".

Request: "{command}"

Location:"""
        return {"location": ask_ai(prompt)}
    
    return {}

def on_begin(self: Type[StreamingClient], event: BeginEvent):
    print(f"🎤 Jarvis listening... (Session: {event.id})")
    print("Say 'Jarvis' to activate commands\n")

def on_turn(self: Type[StreamingClient], event: TurnEvent):
    transcript = event.transcript
    
    # Show what was heard
    print(f"👂 Heard: {transcript}")
    
    # Send to AI for command detection
    request = detect_jarvis_command(transcript)
    
    if request:
        print(f"✅ Jarvis Command: {request}")
        
        # Classify the action type
        action = classify_action(request)
        print(f"🎯 Action: {action}")
        
        # Extract parameters
        params = extract_parameters(request, action)
        if params:
            print(f"⚙️  Parameters: {params}")
        
        print("-" * 50)
        
        # Here you would execute the command
        # execute_command(action, params)
    
    if event.end_of_turn and not event.turn_is_formatted:
        params = StreamingSessionParameters(
            format_turns=True,
        )
        self.set_params(params)

def on_terminated(self: Type[StreamingClient], event: TerminationEvent):
    print(f"\n🛑 Session ended: {event.audio_duration_seconds}s of audio processed")

def on_error(self: Type[StreamingClient], error: StreamingError):
    print(f"❌ Error: {error}")

def main():
    print("="*50)
    print("🤖 JARVIS VOICE ASSISTANT WITH AI")
    print("="*50)
    print("\nMake sure Ollama is running: ollama serve")
    print("Model: qwen2.5:0.5b")
    print("\nExamples:")
    print("  - 'Jarvis, search Google for AI news'")
    print("  - 'Hey Jarvis, what's the weather?'")
    print("  - 'Jarvis, play some music'\n")
    
    client = StreamingClient(
        StreamingClientOptions(
            api_key=api_key,
            api_host="streaming.assemblyai.com",
        )
    )

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True
        )
    )

    try:
        client.stream(
            aai.extras.MicrophoneStream(sample_rate=16000)
        )
    finally:
        client.disconnect(terminate=True)

if __name__ == "__main__":
    main()
