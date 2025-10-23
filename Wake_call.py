import speech_recognition as sr
import random

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Welcome messages
welcome_messages = [
    "Yes, Sir?",
]

# Placeholder functions for testing (replace with actual imports later)
def speak(text):
    print(f"[SPEAK]: {text}")

def listen():
    print("[LISTEN]: Listening...")
    return None

def wake_call():
    while True:

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(" Waiting for wake word 'Jarvis'...")

            try:
                audio = recognizer.listen(source, timeout=None)  # Listen indefinitely

                # Recognize speech using Google Speech Recognition
                Wake_call_input = recognizer.recognize_google(audio).lower()

                if 'jarvis' in Wake_call_input:
                    print(' Jarvis is AWAKE')
                    say = random.choice(welcome_messages)
                    speak(say)
                    print('end')  # Start listening for commands
                    # After listen() returns, go back to waiting for wake word
                    print("\nGoing back to standby...")

            except sr.UnknownValueError:
                print(" Could not understand, keep speaking...")
            except sr.RequestError:
                speak("Speech recognition error. Check your connection.")
            except KeyboardInterrupt:
                speak("Shutting down...")
                break



