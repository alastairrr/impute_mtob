import json
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

QUERIES_FILE = "imputation_queries_length_filtered.json"

api_key = os.getenv("OPENAI_API_KEY")

# Define the API endpoint
url = 'https://api.openai.com/v1/chat/completions'

# Define the headers, including the API key
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}


def main():
    with open(QUERIES_FILE, "r") as file:
        queries = json.load(file)

    with open("preprocessed_wordlist_ke.json", "r") as file:
        word_dict = json.load(file)
    count = 0
    for query_obj in queries:
        query = query_obj["query"]
        print("\n")
        print(query)
        # Define the payload
        payload = {
            "model": "gpt-4o",  # Use the appropriate model name
            "messages": [
                {"role": "user", "content": query}
            ],
            "temperature": 0.05  # Adjust the temperature as needed
        }

        # Convert the payload to a JSON string
        data = json.dumps(payload)

        # Make the POST request to the API
        response = requests.post(url, headers=headers, data=data)

        # Check for a successful response
        if response.status_code == 200:
            try:
                # Parse the JSON response
                response_data = response.json()
                # Print the assistant's reply
                assistant_reply = response_data['choices'][0]['message']['content']
                result = assistant_reply.strip("```json\n").strip("\n```")
                data = json.loads(result)
                print(result)
                # Extract the key-value pairs
                print("imputations:")
                for key, value in data.items():
                    if key not in word_dict["ke"].keys():
                        word_dict["ke"][key] = value
                        print(key, word_dict["ke"][key])
                        count += 1
            except Exception as e:
                print(f"Error: {e}")
        else:
            # Print the error message
            print(f"Error: {response.status_code} - {response.text}")

    print("Number of imputed new words:", count)

    with open(os.path.join("mtob", "resources", "wordlist.json"), 'r') as existing_wordlist_file:
            current_mtob_wordlist = json.load(existing_wordlist_file)
            
    current_mtob_wordlist["ke"].update(word_dict["ke"])

    with open(os.path.join("mtob", "resources", "wordlist.json"), 'w') as existing_wordlist_file:
        json.dump(current_mtob_wordlist, existing_wordlist_file, indent=4)

if __name__ == "__main__":
    main()
