import requests
import base64
import json

def ask_vision(image_path, prompt, model="llama3.2-vision"):
    """Send image and prompt to Ollama vision model"""
    
    # Read and encode image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_data],
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    return response.json()['response']

# Use it
result = ask_vision("/Users/graysonkeenan/Desktop/test_image.jpeg", "What do you see in this image?")


print(result)

