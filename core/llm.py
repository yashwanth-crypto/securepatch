import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b-instruct"

def query_llm(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    result = response.json()
    return result.get("response", "")
