import pygame
import edge_tts
import time 
import asyncio
import threading



async def async_speak(text):
    tts = edge_tts.Communicate(text, "en-GB-RyanNeural")  # Change voice if needed
    await tts.save("output.mp3")


    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    print('saved as file')
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def _speak_sync(text):
    asyncio.run(async_speak(text))

def stop_speak():
    """Stop any currently playing speech audio"""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            print("Speech stopped")
    except:
        print("No audio currently playing")



# Run speak in a background thread so we can interrupt it
def speak(text):
    speak_thread = threading.Thread(target=_speak_sync, args=(text,))
    speak_thread.start()

# Wait 2 seconds then stop the speech
speak('kbj;wejklfejfwefwefwnfewnjfwenjkfenjkefljknefknjlefjlnkefnjlfewjknl')
time.sleep(2)
stop_speak()