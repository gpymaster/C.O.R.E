import requests

_context = None

def ask_ai(prompt, model="qwen2.5:0.5b"):
    """Chat with AI"""
    global _context
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    if _context is not None:
        payload["context"] = _context
    
    response = requests.post(url, json=payload, stream=True)
    
    full_response = ""
    for line in response.iter_lines():
        if line:
            import json
            data = json.loads(line)
            chunk = data.get('response', '')
            print(chunk, end='', flush=True)
            full_response += chunk
            
            if data.get('done'):
                _context = data.get('context')
    
    print()
    return full_response

# Chat loop
print("Chat with qwen2.5:0.5b (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['exit', 'quit']:
        break
    
    print("AI: ", end='')
    ask_ai(user_input)
    print()