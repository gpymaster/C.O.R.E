# #info
# Cognitive Operations & Response Engine
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
from typing import Type
import threading
import time
from google import genai
import pygame
import os
import json
import subprocess
import edge_tts
import asyncio
from llama_text_ai import * 
import speech_recognition as sr
import random
import pygame
import edge_tts
import time
import asyncio
import threading
from llama_text_ai import *
from intent_ai import *
import pywhatkit
import _asyncio
from Weather_api import *


timeout_count = 0
# Initialize speech recognizer
recognizer = sr.Recognizer()



api_key = "b23931700ac540ba96cbe014e532bdb2"

# Configuration
LISTEN_TIMEOUT = 5  # Seconds to wait for speech
SESSION_TIMEOUT = 30  # Seconds of inactivity before requiring wake word again

# Global state
is_listening = False
should_stop = False
last_speech_time = None
received_speech = False
final_transcript = ""
transcript_history = []  # Store last 5 attempts
is_speaking = False  # Track if CORE is currently speaking
in_conversation = False  # Track if we're in an active conversation session
last_interaction_time = None  # Track last user interaction

#GOOGLE AI




def speak(text):
    """Synchronous speak function that runs TTS and plays audio"""
    global is_speaking
    is_speaking = True

    # Create a new event loop for this synchronous context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run the TTS generation
        tts = edge_tts.Communicate(text, "en-GB-RyanNeural")
        loop.run_until_complete(tts.save("output.mp3"))

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load("output.mp3")
        print('saved as file')
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        loop.close()
        is_speaking = False



History_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/History.json'
Action_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/Actions.json'

class history:
    def load():
        with open(History_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["history"]
    def append(text):
        with open(History_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data['history'].append(text)
        with open(History_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return 'added to history'
    def save():
        pass
    
class action_json:
    def read():
        with open(Action_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data['actions'],data['response_format']
        

def listen():
    #global last_interaction_time
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print('Listening.....')
        try:
            audio = recognizer.listen(source)
            User_input = recognizer.recognize_google(audio).lower()
            print(f'Heard: {User_input}')

            Intent(User_input)
            return True  # Successfully heard something

        except sr.WaitTimeoutError:
            print('Session timeout - no speech detected')
            return False  # Timeout occurred
        except sr.UnknownValueError:
            print('I could not understand you, try again....') 
            timeout_count =+ 1
            print(f'add to timout count. whe it reaches 10. it will go into stand by mode')
            print('='*30)
            print(f'count: {timeout_count}')
            listen()
         



from llama_text_ai import *
def Intent(user_input):
    # Get intent name from Ollama

    prompt = f"""Analyze the user's request and return a JSON response with the correct action and parameters.

IMPORTANT DISTINCTIONS:
- search_google: ONLY use when the user explicitly asks to "search google", "look up", "google", or "find on google"
- ask_ai: Use for ALL conversation, knowledge questions, reasoning, discussion, and general queries

Available actions and what they do:
- search_google: Search for information on Google. Use ONLY when user explicitly requests a Google search.
  Requires: 'search' parameter with the search query.
  EXAMPLES: "search google for the weather", "look up flights to NYC", "google best restaurants"

- ask_ai: Answer questions using AI knowledge, have conversations, provide reasoning and explanations.
  Use this for knowledge-based questions, discussions, reasoning, and conversational responses.
  Requires: 'question' parameter with the question to ask.
  EXAMPLES: "how many dogs are in california", "what is quantum physics", "tell me about history", "how do I cook pasta"

- play_song: Play a song. Requires parameter 'song_name' with the name of the song.
- get_time: Get the current time. No parameters needed.
- get_weather: Get the current weather forecast. No parameters needed.

User request: "{user_input}"

DECISION RULE:
1. If user explicitly mentions "google", "search", "look up", or "web search" → use search_google
2. Otherwise → use ask_ai for knowledge, reasoning, conversation, or general questions

Respond ONLY with valid JSON in this format, no other text:
{{
  "action": "one of: search_google, play_song, get_time, get_weather, ask_ai",
  "parameters": null or {{"key": "value"}} if the action needs parameters
}}"""

    response = ask_ollama(prompt)

    # Extract JSON from response
    try:
        intent_json = json.loads(response)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                intent_json = json.loads(json_match.group())
            except:
                intent_json = {"action": "ask_ai", "parameters": {"question": user_input}}
        else:
            intent_json = {"action": "ask_ai", "parameters": {"question": user_input}}

    print(f"\nDetected Intent: {intent_json}")

    # Save to JSON file
    intent_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/intent_response.json'
    with open(intent_file_path, 'w') as f:
        json.dump(intent_json, f, indent=2)
    print(f"Intent saved to: {intent_file_path}")
    Understand_intent(intent_json)
from llama_text_no_history import *

def Understand_intent(intent_data):
    """Execute actions based on the detected intent"""
    response = intent_data

    if 'search_google' in response['action']:
        if response['parameters'] and 'search' in response['parameters']:
            print('working....')
            pywhatkit.search(response['parameters']['search'])

    if 'play_song' in response['action']:
        if response['parameters'] and 'song_name' in response['parameters']:
            text = response['parameters']['song_name']
            print(f'pretending to play song: {text}')
            # #end-todo
            # Add function to actually play a song here

    if 'get_time' in response['action']:
        import datetime
        from zoneinfo import ZoneInfo
        now = datetime.datetime.now(ZoneInfo("America/Los_Angeles"))
        formatted_time_12hr = now.strftime("%I:%M:%S %p")
        speak(f"The current time is {formatted_time_12hr}")

    if 'get_weather' in response['action']:
        weather_info = asyncio.run(main())
        speak(str(weather_info))

    if 'ask_ai' in response['action']:
        if response['parameters'] and 'question' in response['parameters']:
            print('=>'*100)
            main_c()
            print('=>'*100)


    
    

from Converstion_action import * 

    




def wake_call():
    global in_conversation, last_interaction_time

    while True:
        if not in_conversation:
            # Wake word mode - wait for "Jarvis"
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                print(" Waiting for wake word 'Jarvis'...")

                try:
                    audio = recognizer.listen(source, timeout=None)  # Listen indefinitely

                    # Recognize speech using Google Speech Recognition
                    Wake_call_input = recognizer.recognize_google(audio).lower()

                    if 'jarvis' in Wake_call_input:
                        print(' Jarvis is AWAKE')
                        in_conversation = True
                        last_interaction_time = time.time()
                        say = ("yes Sir?")
                        speak(say)
                        # Don't call listen() here, let the loop handle it
                except sr.UnknownValueError:
                    print(" Could not understand, keep speaking...")
                except sr.RequestError:
                    speak("Speech recognition error. Check your connection.")
                except KeyboardInterrupt:
                    speak("Shutting down...")
                    break
        else:
            # Conversation mode - keep listening without wake word
            print(" In conversation mode (will timeout after {} seconds of silence)".format(SESSION_TIMEOUT))

            # Listen for user input
            continue_session = listen()

            if not continue_session:
                # Timeout occurred, exit conversation mode
                print(" Session timed out. Going back to sleep...")
                speak("Going back to sleep. Say Jarvis to wake me.")
                in_conversation = False
                last_interaction_time = None










# TODDO
# listen and action function
# Wake call function
# interuption calls
    #thread listening
#-----------------------------------
# A.I
#-----------------------------------
# Reasoning
# memory
# actions
# Master json
#  |
#  \/
# Action systems



Intent('how are u today')

'''
NOTES:
while I am asking a question or it is just waiting.
the second ai will update the json dependding on what I said and there will be make thread that will always if somthing is true in the json and
that will set of a thread and do somthing



while in stand by mode, outward notifictions. it will always check if it needs to notfi user
if so, it does then goes into converstatio mode/ask ai, and the ai will have what it just said and based on what we are talking about it will check is it needs a action

'''