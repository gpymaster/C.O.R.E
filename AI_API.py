#-----API KEY----
from groq import Groq
import os

# Initialize Groq client
client = Groq(
    api_key="-----API KEY----"  # Replace with your actual API key
)

def chat(user_message, conversation_history=None):

    if conversation_history is None:
        conversation_history = []
    
    # Add the new user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Create streaming chat completion
    stream = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024,
        stream=True  # Enable streaming
    )
    
    # Collect and display the streaming response
    full_response = ""
    
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    print()  # New line after streaming completes
    
    # Add assistant's response to history
    conversation_history.append({
        "role": "assistant",
        "content": full_response
    })
    
    return full_response, conversation_history


print(chat('how are u today. can you help me with homework',None))