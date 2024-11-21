import json 
import re
import os
from tap import Tap

class Args(Tap):
    alpha: float = 0.5
    alpha_level: str = "character"

def display_jsonify(data: dict) -> None:
    print(json.dumps(data, indent=4))

def sentence_splitter_character_level(sentence_source: str, sentence_target: str, wordlist: dict, include_named_entities: bool=True) -> list:
    words = sentence_source.split()
    target_split = re.sub(r'[^a-zA-Z0-9\s]', '', sentence_target).split()

    split = []
    i = 0
    while i < len(words):
        if i < len(words) - 1 and f"{words[i]} {words[i+1]}" in wordlist:
            split.append(f"{words[i]} {words[i+1]}")
            i += 2
        else:
            split.append(words[i])
            i += 1
    result = []
    for word in split:
        cleaned_word = re.sub(r'[^a-zA-Z0-9]', '', word)
        # check if it's a named entity
        if word in target_split and include_named_entities == True:
            result.append(word)
        elif word in wordlist:
            result.append(word)
        elif cleaned_word in wordlist:
            result.append(cleaned_word)
        elif cleaned_word.lower() in wordlist:
            result.append(cleaned_word.lower())
        else:  # Word Break
            cleaned_word = "#" + cleaned_word.lower() + "#"
            dp = [False] * (len(cleaned_word) + 1)
            dp[len(cleaned_word)] = True
            for i in range(len(cleaned_word) - 1, -1, -1):
                for w in wordlist:
                    if len(w) > 2:
                        if (i + len(w)) <= len(cleaned_word) and cleaned_word[i:i+len(w)] == w:
                            dp[i] = dp[i + len(w)]
                        if dp[i]:
                            if len(w) > 3: # ignore affixes or subwords less than 4 characters to prevent likelihood of hallucination 
                                result.append(w)
                            break
    return result

def sentence_splitter_word_level(sentence_source: str, sentence_target: str, wordlist: dict, include_named_entities: bool=True) -> list:
    words = sentence_source.split()
    target_split = re.sub(r'[^a-zA-Z0-9\s]', '', sentence_target).split()

    split = []
    i = 0

    while i < len(words):
        if i < len(words) - 1 and f"{words[i]} {words[i+1]}" in wordlist:
            split.append(re.sub(r'[^a-zA-Z0-9\s]', '', f"{words[i]} {words[i+1]}"))
            i += 2
        else:
            split.append(re.sub(r'[^a-zA-Z0-9\s]', '', words[i]))
            i += 1

    result = []
    for word in split:
        cleaned_word = re.sub(r'[^a-zA-Z0-9\s]', '', word)
        # check if it's a named entity
        if word in target_split and include_named_entities == True:
            result.append(word)
        elif word in wordlist:
            result.append(word)
        elif cleaned_word in wordlist:
            result.append(cleaned_word)
        elif cleaned_word.lower() in wordlist:
            result.append(cleaned_word.lower())
        else:  # Word Break
            subwords = []
            cleaned_word = "#" + cleaned_word.lower() + "#"
            dp = [False] * (len(cleaned_word) + 1)
            dp[len(cleaned_word)] = True
            for i in range(len(cleaned_word) - 1, -1, -1):
                for w in wordlist:
                    if len(w) > 2:
                        if (i + len(w)) <= len(cleaned_word) and cleaned_word[i:i+len(w)] == w:
                            dp[i] = dp[i + len(w)]
                        if dp[i]:
                            if len(w) > 3: # ignore affixes or subwords less than 4 characters to reduce likelihood of hallucination 
                                subwords.append(w)
                            break
            result.append(subwords)
    return result, split

def compute_word_level_alpha(segmentation_set, expected_splits):
    word_score = 0
    for count, segmentation_word in enumerate(segmentation_set):

        # whole matches
        if isinstance(segmentation_word, str):
            if segmentation_word.lower() in [expected_word.lower() for expected_word in expected_splits]:
                word_score += 1

        # accounting for partial subword matches, which are wrapped in a list
        elif isinstance(segmentation_word, list):
            rejoined_string = ''.join(segmentation_word).replace('#', '')
                
            score = len(rejoined_string) / len(expected_splits[count])
            word_score += score if score <= 1 else 1

    return word_score / len(expected_splits)

def refactor_split(segmentation_split, wordlist):
    result = []
    for word in segmentation_split:
        if isinstance(word, str):
            if word not in result:
                result.append(word)
        elif isinstance(word, list):
            result.extend(word)
    split = []
    i = 0
    while i < len(result):
        if i < len(result) - 1 and f"{result[i]} {result[i+1]}" in wordlist:
            split.append(f"{result[i]} {result[i+1]}")
            i += 2
        else:
            split.append(result[i])
            i += 1
    return split

def main() -> None:
    args = Args().parse_args()

    DIRECTION = "ke"

    SOURCE_KEY = "translation"
    TARGET_KEY = "original"
    SENTENCE_PAIR_FILE =  os.path.join("mtob", "splits", "train_examples.json")

    WORDLIST_FILE = os.path.join("preprocessed_wordlist_ke.json")

    with open(SENTENCE_PAIR_FILE, "r") as file:
        train_examples = json.load(file)
    #display_jsonify(train_examples[1])

    with open(WORDLIST_FILE, "r") as file:
        word_dict = json.load(file)
    kal_wordlist = list(word_dict[DIRECTION].keys())

    queries = []

    for sample in train_examples:
        if "big-bench-canary" in sample:
            continue
            
        print("Sample:", sample["original_id"])
        print("Source:\"", sample[SOURCE_KEY], "\"")
        print("Target:\"", sample[TARGET_KEY], "\"")

        split = None

        if args.alpha_level == "character":
            expected_split = re.sub(r'[^a-zA-Z0-9\s]', '', sample[SOURCE_KEY]).split()
            print("expected_split:", str(expected_split))
            sentence_split = sentence_splitter_character_level(sample[SOURCE_KEY], sample[TARGET_KEY], kal_wordlist) # only for alpha ratio calculation
            alpha_ratio = len(re.sub(r'[^a-zA-Z0-9]', '', "".join(sentence_split))) / len(re.sub(r'[^a-zA-Z0-9]', '', sample[SOURCE_KEY]))
            split = sentence_splitter_character_level(sample[SOURCE_KEY], sample[TARGET_KEY], kal_wordlist, include_named_entities=False)
            
        elif args.alpha_level == "word":

            sentence_split, expected = sentence_splitter_word_level(sample[SOURCE_KEY], sample[TARGET_KEY], kal_wordlist, include_named_entities=False)
            print("expected_split:", expected)
            
            assert len(sentence_split) == len(expected), f"Length mismatch: {len(sentence_split)} != {len(expected)}"

            alpha_ratio = compute_word_level_alpha(sentence_split, expected)
            split = refactor_split(sentence_split, kal_wordlist)

        print("naive_resultant_split:", split)

        print("\n")
        if alpha_ratio > args.alpha:
            query_construct = {"query": f"Given the following sentence in Kalamang and the English translation, find the missing Kalamang words in the dictionary list and the equivalent English definitions.\nSentence: {sample[SOURCE_KEY]}\nTranslation: {sample[TARGET_KEY]}\nwordlist: {str([{split[i]: word_dict[DIRECTION][split[i].lower()] if split[i].lower() in word_dict[DIRECTION] else word_dict[DIRECTION][split[i]]} for i in range(len(split))]).strip('[]')}\nOnly output the missing Kalamang words as the key and the list [English word type, English definition] as the value in a JSON structure:", "id": sample["original_id"]}
            queries.append(query_construct)


    print(len(queries))

    with open('imputation_queries_length_filtered.json', 'w') as json_file:
        json.dump(queries, json_file, indent=4)

if __name__ == "__main__":
    main()