import json 
import os

unique_keys = []

def display_jsonify(data: dict) -> None:
    print(json.dumps(data, indent=4))

def modify_key(key):
    if key.startswith("-") or key.startswith("="):
        key = key[1:] + "#"
    elif key.endswith("-") or key.endswith("="):
        key = "#" + key[0:-1]     
    if key not in unique_keys:
        unique_keys.append(key)
    else:
        print(key)
    return key

def main() -> None:
    DIRECTION = "ke"
    WORDLIST_FILE = os.path.join("mtob", "resources","wordlist.json")

    with open(WORDLIST_FILE, "r") as file:
        word_dict = json.load(file)
    modified_data = {DIRECTION: {modify_key(key): value for key, value in word_dict[DIRECTION].items()}}

    with open('preprocessed_wordlist_ke.json', 'w') as json_file:
        json.dump(modified_data, json_file, indent=4)
        
if __name__ == "__main__":
    main()