import requests

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"

def analyze(text):
    prompt = f"""Classify the following content as "Toxic" or "Not Toxic". 
Respond in JSON with a key 'toxicity' and a confidence percentage.
Content: \"{text}\""""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()
