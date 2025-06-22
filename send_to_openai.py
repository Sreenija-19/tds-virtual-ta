import requests
import json
import os

# Replace with your actual OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Endpoint
url = "https://api.openai.com/v1/chat/completions"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# JSON body (copied from the canvas)
data = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "Respond in JSON"
        },
        {
            "role": "user",
            "content": "Generate 10 random addresses in the US"
        }
    ]
}

# Make the API request
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    print(json.dumps(result, indent=2))
    # Save to file for easier inspection
    with open("openai_response.json", "w") as f:
        json.dump(result, f, indent=2)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    with open("openai_response.json", "w") as f:
        f.write(f"HTTP error occurred: {http_err}\n{response.text}")
except Exception as err:
    print(f"Other error occurred: {err}")
    with open("openai_response.json", "w") as f:
        f.write(f"Other error occurred: {err}")