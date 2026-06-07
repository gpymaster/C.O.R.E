from llama_text_no_history import*
import json
import pygame
import asyncio
import edge_tts
import pywhatkit

History_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/History.json'
test_json_path = '/Users/graysonkeenan/Desktop/C.O.R.E/Conversation_json.json'


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

def understand_json_converstation():
    with open(test_json_path, "r", encoding="utf-8") as f:
            json_con = json.load(f)
            if (json_con["action"]) == 'NONE':
                print('no action needed')
                #speak(json_con["ai_conversation_response"])
            elif json_con["action"] == 'search_google':
                print('searching...')
                pywhatkit.search(json_con["parameters"])
                #speak(json_con["ai_conversation_response"])

                


def converastion(ask):
    ask_n = ask
    ai = ask_ollama_NH(f'''IMPORTANT: You MUST respond ONLY in valid JSON format. No other text before or after.

    You are having a conversation with a user. Always respond in this exact JSON structure:
    {{
        "action": "action_name_or_none",
        "parameters": "parameter_value_or_none",
        "ai_conversation_response": "Your conversational response to the user"
    }}
    These are the action you can pick from, IF one is needed
        search_google
        get_weather
        get_time
        
    Guidelines:
    - PRIORITY: Always have a natural conversation first
    - "action" values: search_weather, search_google, or NONE
    - Only use an action if: you cannot answer the question without it, OR the user explicitly asks for one
    - "parameters": relevant search terms or values, or NONE if no action needed
    - "ai_conversation_response": This is your main response - always make it conversational and helpful

    Examples:
    1. User: "What are some good running shoes for track?"
    Response: {{"action": "NONE", "parameters": "NONE", "ai_conversation_response": "I recommend Nike Vaporfly or Asics Metaspeed for track. They're lightweight with excellent spike support. Nike Vaporfly is great for sprinting while Asics Metaspeed is better for long-distance track events."}}

    2. User: "Where can I find those shoes?"
    Response: {{"action": "search_google", "parameters": "Nike Vaporfly track shoes price", "ai_conversation_response": "Let me search for where you can buy those. I'll look for the best prices and retailers available."}}

    3. User: "What's the weather like?"
    Response: {{"action": "search_weather", "parameters": "current location", "ai_conversation_response": "Let me check the weather for you right now."}}


    *** remember that is you think you can repsonde with out a action needed, just put your repsonse in the ai reposnse area in the json output.       
    **** to make it more converstaion. lets talk for a while and repsonse if you can on your own then if I want u todo somthing or u think there should be a action do it.                                           
            
    REMEMBER: Return ONLY valid JSON, nothing else.
    REMEMBER: You can respond as an AI without any action needed. If you can fully answer a question, do so without an action. Only include an action if the user explicitly asks for one or if future context suggests an action would be helpful.

    Example:
    User: "What running shoes should I get for track?"
    AI: {{"action": "NONE", "parameters": "NONE", "ai_conversation_response": "I recommend Nike Vaporfly for track events. They're designed with lightweight materials and excellent spike support, making them ideal for sprinting and jumping events."}}

    User: "Where can I find those?"
    AI: {{"action": "search_google", "parameters": "Nike Vaporfly track shoes", "ai_conversation_response": "Let me search for where you can buy those."}}
                    

    User input: {ask_n}

    Here is the history of our past converstation: so it could be connected to what your just said or and my repsonse {history.load()}

    this is a new converastion, this history is just for context



    '''
    )



    history.append(f'user input:{ask_n},ai repsonse: {ai}')
    history.save()



    try:
        json_response = json.loads(ai)
        print("\n[Parsed Response]")
        print(json.dumps(json_response, indent=2))

        # Save to test.json
        with open(test_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_response, f, indent=2)
        print("[Saved to test.json]")
        understand_json_converstation()
        
    except json.JSONDecodeError:
        print("\n[Warning: Response was not valid JSON]")
        print(ai)

def main_c():
    while True:
        text = input('enter:')
        converastion(text)
