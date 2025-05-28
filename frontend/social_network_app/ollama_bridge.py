import requests
import pytesseract
from PIL import Image

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"

def analyze(text,files,images):
    content = text

    prompt = f"""Classify the following content as "Toxic" or "Not Toxic". 
    Respond in JSON with a key 'toxicity' and a confidence percentage.
    Content: \"{content}\""""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Ollama API error:", str(e))
        print("❗ Response text:", response.text if 'response' in locals() else "No response")
        return {"response": '{"toxicity": "Not Toxic", "confidence": "0%"}'}
