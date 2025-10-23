import os
import requests
import json
from typing import List

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "History.json")


def load_history() -> List[str]:
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("history"), list):
                return [str(x) for x in data.get("history")]
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return []


def save_history_entry(question: str, answer: str, max_items: int = 200) -> None:
    hist = load_history()
    entry = f"Question:{question},Answer:{answer}\n"
    hist.append(entry)
    if len(hist) > max_items:
        hist = hist[-max_items:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": hist}, f, indent=2, ensure_ascii=False)
    except Exception:
        # best-effort save; ignore errors
        pass


def ask_ollama(text: str, model: str = "llama3.2", enable_history: bool = True) -> str:
    
    url = "http://localhost:11434/api/generate"

    history = load_history() if enable_history else []
    prompt = text
    if enable_history and history:
        # include simple text history for context
        history_text = "\n".join(history)
        prompt = f"{history_text}\nQuestion: {text}"

    payload = {"model": model, "prompt": prompt, "stream": True}

    try:
        response = requests.post(url, json=payload, stream=True, timeout=60)
    except Exception as e:
        return f"ERROR: could not connect to Ollama at {url}: {e}"

    full_response = ""
    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
                chunk = data.get("response", "")
            except Exception:
                chunk = line
            # print(chunk, end="", flush=True)
            full_response += chunk
    except Exception:
        # fallback to full text
        try:
            full_response = response.text
        except Exception:
            full_response = ""

    # persist history
    if enable_history:
        try:
            save_history_entry(text, full_response)
        except Exception:
            pass

    return full_response


