import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Before running, please change the below settings:
MANUAL_QUERY = "" # Add the manual query here 
MODEL_TYPE = "gpt-4" # Add the model type here
ENDPOINT = 'https://api.openai.com/v1/chat/completions' # Define the API endpoint

# ----------------------------

api_key = os.getenv("OPENAI_API_KEY")


headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

payload = {
    "model": MODEL_TYPE,  # Use the appropriate model name
    "messages": [
        {"role": "user", "content": MANUAL_QUERY.replace("Now write the translation.", "Now write the translation. Output the translation only. If you are not sure what the translation should be, then give your best guess. Do not say that you do not speak Kalamang. If your translation is wrong, that is fine, but you have to provide a translation.")}
    ],
    "temperature": 0.05  # Adjust the temperature as needed
}

data = json.dumps(payload)

# Make the POST request to the API
response = requests.post(ENDPOINT, headers=headers, data=data)

# Check for a successful response
if response.status_code == 200:
    try:
        # Parse the JSON response
        response_data = response.json()
        # Print the assistant's reply
        assistant_reply = response_data['choices'][0]['message']['content']
        result = assistant_reply
        print(result)

    except Exception as e:
        print(f"Error: {e}")
else:
    # Print the error message
    print(f"Error: {response.status_code} - {response.text}")

print("\n")