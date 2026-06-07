import requests

WIT_ACCESS_TOKEN = "-----API KEY----"
WIT_API_URL = "https://api.wit.ai/message?v=20230220&q="

# Function to get intent from Wit.ai
def get_intent(user_input):
    headers = {"Authorization": f"Bearer {WIT_ACCESS_TOKEN}"}
    response = requests.get(WIT_API_URL + user_input, headers=headers)

    if response.status_code == 200:
        data = response.json()
        intents = data.get("intents", [])

        if intents:
            return intents[0]["name"]  # Get the highest-confidence intent
        else:
            return "unknown"
    else:
        return "error"

