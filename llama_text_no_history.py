import requests
import json

_context = None

def ask_ollama_NH(prompt, model="llama3.2"):
    """Ask Ollama with streaming response"""
    global _context
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    if _context is not None:
        payload["context"] = _context
    
    try:
        response = requests.post(url, json=payload, stream=True)
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                chunk = data.get('response', '')
                print(chunk, end='', flush=True)
                full_response += chunk
                
                if data.get('done'):
                    _context = data.get('context')
        
        print()  # New line
        return full_response
    
    except Exception as e:
        return f"Error: {e}"

# Usage

