from llama_text_no_history import*
import json

History_file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/History.json'
test_json_path = '/Users/graysonkeenan/Desktop/C.O.R.E/test.json'

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




ask_n = 'what are the best running shoes for track and high jumps'
ai = ask_ollama_NH(f'''IMPORTANT: You MUST respond ONLY in valid JSON format. No other text before or after.

You are having a conversation with a user. Always respond in this exact JSON structure:
{{
    "action": "action_name_or_none",
    "parameters": "parameter_value_or_none",
    "ai_conversation_response": "Your conversational response to the user"
}}

Guidelines:
- "action" values: search_weather, search_google, calculate, or NONE
- "parameters": relevant search terms or values, or NONE if no action needed
- "ai_conversation_response": Always include a natural conversational response

Examples:
1. User: "Search for the weather"
   Response: {{"action": "search_weather", "parameters": "current location", "ai_conversation_response": "I'll check the weather for you."}}

2. User: "What is 2+2?"
   Response: {{"action": "NONE", "parameters": "NONE", "ai_conversation_response": "2+2 equals 4."}}

3. User: "What are some good running shoes?"
   Response: {{"action": "search_google", "parameters": "best running shoes", "ai_conversation_response": "I found some great running shoe options for you. Let me pull up some recommendations."}}


*** remember that is you think you can repsonde with out a action needed, just put your repsonse in the ai reposnse area in the json output.       
**** to make it more converstaion. lets talk for a while and repsonse if you can on your own then if I want u todo somthing or u think there should be a action do it.                                           
        
REMEMBER: Return ONLY valid JSON, nothing else.

User input: {ask_n}

Here is the history of our past converstation: {history.load()}

this is a new converastion, this history is just for context



'''
)



history.append(f'user input:{ask_n},ai repsonse: {ai}')
history.save()


    # Try to parse and save the JSON response
# try:
#     json_response = json.loads(response)
#     print("\n[Parsed Response]")
#     print(json.dumps(json_response, indent=2))

#     # Save to test.json
#     with open(test_json_path, 'w', encoding='utf-8') as f:
#         json.dump(json_response, f, indent=2)
#     print("[Saved to test.json]")
# except json.JSONDecodeError:
#     print("\n[Warning: Response was not valid JSON]")
#     print(response)