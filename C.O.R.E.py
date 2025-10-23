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
            return 'added to history'
    def save():
        with open(History_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(History_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
class action_json:
    def read():
        with open(Action_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data['actions'],data['response_format']
        
        # hello this is a new bracnch to see if this works



def listen():
    global last_interaction_time
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print('Listening')
        try:
            audio = recognizer.listen(source, timeout=SESSION_TIMEOUT)
            User_input = recognizer.recognize_google(audio).lower()
            last_interaction_time = time.time()  # Update last interaction time
            Intent(User_input)
            return True  # Successfully heard something

        except sr.WaitTimeoutError:
            print('Session timeout - no speech detected')
            return False  # Timeout occurred
        except sr.UnknownValueError:
            print('I could not understand you, try again....')
            last_interaction_time = time.time()  # Reset timer even on unclear speech
            return True  # Keep session active

            #Intent(User_input)

def Intent(user_input):
    # Get intent name from Wit.ai
    intent_name = get_intent(user_input)

    print(f"\nDetected Intent: {intent_name}")

    # Create intent JSON structure
    intent_json = {"action": intent_name, "parameters": None}

    # Save to JSON file
    intent_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/intent_response.json'
    with open(intent_file_path, 'w') as f:
        json.dump(intent_json, f, indent=2)
    print(f"Intent saved to: {intent_file_path}")

    Understand_intent(intent_json)
    return intent_json

def Understand_intent(intent_data):
    """Execute actions based on the detected intent"""
    response = intent_data

    if 'search_google' in response['action']:
        if response['parameters'] and 'search' in response['parameters']:
            print('working....')
            pywhatkit.search(response['parameters']['search'])
        else:
            speak("What would you like me to search for?")

    if 'play_song' in response['action']:
        if response['parameters'] and 'song_name' in response['parameters']:
            text = response['parameters']['song_name']
            print(f'pretending to play song: {text}')
            # #end-todo
            # Add function to actually play a song
        else:
            speak("What song would you like me to play?")

    if 'get_time' in response['action']:
        import datetime
        now = datetime.datetime.now()
        formatted_time_12hr = now.strftime("%I:%M:%S %p")
        speak(f"The current time is {formatted_time_12hr}")

    if 'get_weather' in response['action']:
        weather_info = asyncio.run(main())
        speak(str(weather_info))

    if 'ask_ai' in response['action']:
        if response['parameters'] and 'question' in response['parameters']:
            answer = ask_ollama(response['parameters']['question'])
            print(answer)
        else:
            speak("I didn't catch your question. Could you please repeat that?")
    
    



    

    


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




Intent("hey jarvis, how any miles are from the earth to the sun")

'''
NOTES:
while I am asking a question or it is just waiting.
the second ai will update the json dependding on what I said and there will be make thread that will always if somthing is true in the json and
that will set of a thread and do somthing



while in stand by mode, outward notifictions. it will always check if it needs to notfi user
if so, it does then goes into converstatio mode/ask ai, and the ai will have what it just said and based on what we are talking about it will check is it needs a action

'''